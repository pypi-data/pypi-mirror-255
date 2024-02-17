import collections
import copy
import gc
import os
import pathlib
import typing
import time
import shutil
import warnings
from zipfile import ZipFile

import yaml

from remotemanager.dataset.lazy_append import LazyAppend
from remotemanager.storage.remotefunction import cached_functions
from remotemanager.connection.url import URL
from remotemanager.storage.database import Database
from remotemanager.storage.function import Function
from remotemanager.dataset.runner import Runner, localwinerror
import remotemanager.transport as tp
import remotemanager.serialisation as sr
from remotemanager.connection.cmd import CMD
from remotemanager.storage import SendableMixin, TrackedFile
from remotemanager.utils.uuid import generate_uuid
from remotemanager.utils import (
    get_version,
    ensure_list,
    ensure_filetype,
    check_dir_is_child,
)
from remotemanager.logging.utils import format_iterable
from remotemanager.dataset.dependency import Dependency
from remotemanager.logging import LoggingMixin
from remotemanager.logging.verbosity import Verbosity
from remotemanager.logging.quiet import Quiet


class Dataset(SendableMixin, LoggingMixin):
    """
    Bulk holder for remote runs. The Dataset class handles anything regarding
    the runs as a group. Running, retrieving results, sending to remote, etc.

    Args:
        function (Callable):
            function to run
        url (URL):
            connection to remote (optional)
        transport (tp.transport.Transport):
            transport system to use, if a specific is required. Defaults to
            transport.rsync
        serialiser (serial.serial):
            serialisation system to use, if a specific is required. Defaults
            to serial.serialjson
        script (str):
            callscript required to run the jobs in this dataset
        submitter (str):
            command to exec any scripts with. Defaults to "bash"
        name (str):
            optional name for this dataset. Will be used for runscripts
        extra_files_send(list, str):
            extra files to send with this run
        extra_files_recv(list, str):
            extra files to retrieve with this run
        skip (bool):
            skip dataset creation if possible. Defaults True
        extra:
            extra text to insert into the runner jobscripts
        global_run_args:
            any further (unchanging) arguments to be passed to the runner(s)

    Attributes:
        default_url (URL):
            a default url can be assigned to all Datasets.
    """

    _do_not_package = ["_database"]

    _manifest_file = "archive_manifest.txt"

    default_url = None

    # DEV NOTE: arguments must be None for computer-url override to function
    def __init__(
        self,
        function: [typing.Callable, str],
        url: URL = None,
        dbfile: str = None,
        transport: tp.transport.Transport = None,
        serialiser: sr.serial = None,
        script: str = None,
        shebang: str = None,
        name: str = None,
        extra_files_send: list = None,
        extra_files_recv: list = None,
        verbose: int = None,
        add_newline: bool = True,
        skip: bool = True,
        extra: str = None,
        **global_run_args,
    ):
        self._verbose = Verbosity(verbose)

        self._logger.info("dataset initialised")

        self._function = Function(function)

        self._global_run_args = copy.deepcopy(Runner._defaults)
        # sanitise paths
        if "remote_dir" in global_run_args:
            global_run_args["remote_dir"] = self.sanitise_path(
                global_run_args["remote_dir"]
            )
        if "run_dir" in global_run_args:
            global_run_args["run_dir"] = self.sanitise_path(global_run_args["run_dir"])
        if "local_dir" in global_run_args:
            global_run_args["local_dir"] = self.sanitise_path(
                global_run_args["local_dir"]
            )

        self._global_run_args.update(global_run_args)
        self._global_run_extra = extra

        # dataset uuid is equal to Function uuid for now
        self._name = name or "dataset"
        self._uuid = generate_uuid(self._function.uuid + self.name)
        self._logger.info(f"uuid is {self.uuid}")

        self._extra_files = {
            "send": ensure_list(extra_files_send)
            if extra_files_send is not None
            else [],
            "recv": ensure_list(extra_files_recv)
            if extra_files_recv is not None
            else [],
        }
        self._add_newline = add_newline

        self._last_run = -1

        self._url = None
        self._transport = None
        self._computer = False
        self._serialiser = None
        self._dependency = None
        self._do_not_recurse = False

        self._dbfile_override = dbfile

        if "dataset" in self.name.lower():
            dbfile_base = f"{self.name}-{self.short_uuid}"
        else:
            dbfile_base = f"dataset-{self.name}-{self.short_uuid}"

        self._dbfile = ensure_filetype(dbfile_base, "yaml")

        if url is None:
            self.url = self.default_url
        else:
            self.url = url
        self.transport = transport
        self.serialiser = serialiser
        self._submitter = None

        self._script = script or ""
        # Dataset shebang takes priority _only_ if manually set
        if shebang is not None:
            self.shebang = shebang

        if not skip:
            try:
                os.remove(self.dbfile)
                self._logger.warning(
                    f"deleted database file {self.dbfile}", silent=True
                )
            except FileNotFoundError:
                self._logger.warning(
                    f"could not delete database at {self.dbfile} (FileNotFoundError)",
                    silent=True,
                )

        self._run_cmd = None
        self._repo_files = []
        self._master_scripts = []
        if skip and os.path.isfile(self.dbfile):
            self._create_from_db()
        else:
            self._create_fresh()

        self._append_log = {}
        self._append_session = 0
        self._run_summary_limit = 25
        self._run_log = []

        self._logger.info(f"Dataset {self.name} init complete")

    def _create_from_db(self):
        self._logger.info(f"unpacking database from {self.dbfile}")

        # create a "temporary" database from the found file
        self._database = Database(self.dbfile)
        old_uuid = next(iter(self._database._storage))  # get uuid by first key
        self._logger.info(f"unpacked uuid is {old_uuid}")
        if old_uuid != self.uuid:
            self._logger.debug(f"current uuid is {self.uuid}")
            dst = f"{self.dbfile}.old"

            dst = self.database.backup(dst)

            self._logger.warning(
                "new and old UUID mismatch "
                "(did something change?)\n"
                "Creating a fresh dataset and backing up the "
                f"old dbfile at {dst}. \nUse "
                f"Dataset.from_file('{dst}') to recover the "
                f"old dataset."
            )
            return self._create_fresh()
        # update it with any new values
        self.database.update(self.pack())
        # unpack from here to retrieve
        payload = self.database._storage[self.uuid]
        self.inject_payload(payload)

    def _create_fresh(self):
        self._logger.info("No database file found, creating anew")
        self._runs = collections.OrderedDict()
        self._uuids = []
        self._results = []

        # database property creates the database if it does not exist
        self.database._storage = {}
        self.database.update(self.pack())

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.uuid == other.uuid

    def __repr__(self):
        return f"dataset-{self.name}-{self.short_uuid}"

    @classmethod
    def recreate(cls, raise_if_not_found: bool = True, *args, **kwargs):
        """
        Attempts to extract a dataset matching the given args from the python
        garbage collection interface

        Args:
            raise_if_not_found (bool):
                raise ValueError if the Dataset was not found
            *args:
                args as passed to Dataset
            **kwargs:
                keyword args as passed to Dataset
        Returns:
            Dataset
        """

        for obj in gc.get_objects():
            if isinstance(obj, cls):
                tmp = cls(*args, **kwargs)
                if obj == tmp:
                    print("returning stored obj")
                    return obj

        if raise_if_not_found:
            raise ValueError("Dataset with args not found!")

        return cls(*args, **kwargs)

    @classmethod
    def from_file(cls, file: str):
        """
        Alias for Dataset.unpack(file=...)

        Args:
            file (str):
                Dataset dbfile

        Returns:
            (Dataset): unpacked Dataset
        """
        return Dataset.unpack(file=file)

    @property
    def verbose(self) -> Verbosity:
        """
        Return the current verbosity setting

        Returns:
            (Verbosity): current verbosity
        """
        return self._verbose

    @verbose.setter
    def verbose(self, verbose) -> None:
        """
        Verbosity setter
        """
        self._verbose = Verbosity(verbose)

    @property
    def database(self) -> Database:
        """
        Access to the stored database object.
        Creates a connection if none exist.

        Returns (Database):
            Database
        """
        if self.is_missing("_database"):
            self._logger.debug(
                f"Database missing, regenerating from file {self.dbfile}"
            )
            payload = self.pack()
            payload[Database._versionkey] = get_version()
            with open(self.dbfile, "w+") as o:
                yaml.dump(payload, o)

            self._database = Database(file=self.dbfile)
        return self._database

    @property
    def dbfile(self) -> str:
        """
        Name of the database file
        """
        if self._dbfile_override is not None:
            return ensure_filetype(self._dbfile_override, "yaml")
        return self._dbfile

    @dbfile.setter
    def dbfile(self, file: str) -> None:
        """
        Moves the stored database to `file`.

        Args:
            file:
                new file path
        """
        self._logger.debug(f"updating dbfile to {file}")
        self.update_db()  # make sure the database is valid
        # make sure new path is valid
        path = ensure_filetype(file, "yaml")
        # move the old database to the new location
        shutil.move(self.dbfile, path)
        self._logger.debug(f"moved {self.dbfile} to {path}")
        self._dbfile = path  # update internal path

    @staticmethod
    def sanitise_path(path):
        path = str(pathlib.PureWindowsPath(path).as_posix())

        if " " in path:
            raise ValueError(f"Space character detected in path {path}")

        return path

    @property
    def remote_dir(self) -> [str, bool]:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        return self.global_run_args.get("remote_dir", Runner._defaults["remote_dir"])

    @remote_dir.setter
    def remote_dir(self, path):
        self._global_run_args["remote_dir"] = path

        self.update_db()

    @property
    def run_dir(self) -> [str, bool]:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        return self.global_run_args.get("run_dir", None)

    @run_dir.setter
    def run_dir(self, path):
        self._global_run_args["run_dir"] = path

        self.update_db()

    @property
    def run_path(self) -> [str, bool]:
        """
        Accesses the remote_dir property from the run args. Tries to fall back
        on run_dir if not found, then returns default as a last resort.
        """
        return os.path.join(self.remote_dir, self.run_dir)

    @property
    def local_dir(self) -> str:
        """
        Accesses the local_dir property from the run args. Returns default if
        not found.
        """
        return self.global_run_args.get("local_dir", Runner._defaults["local_dir"])

    @local_dir.setter
    def local_dir(self, path):
        self._global_run_args["local_dir"] = path

        self.update_db()

    @property
    def repofile(self) -> TrackedFile:
        fname = f"{self.name}-{self.short_uuid}-repo.py"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def master_script(self) -> TrackedFile:
        fname = f"{self.name}-{self.short_uuid}-master.sh"
        return TrackedFile(self.local_dir, self.remote_dir, fname)

    @property
    def main_dir_env(self):
        return f"DATASET_{self.short_uuid}_MAIN_DIR"

    @property
    def argfile(self) -> str:
        return f"args-{self.name}-{self.short_uuid}"

    @property
    def global_run_args(self):
        return self._global_run_args

    @property
    def run_args(self):
        return self._global_run_args

    def set_run_arg(self, key: str, val):
        """
        Set a single run arg `key` to `val`

        Args:
            key:
                name to set
            val:
                value to set to

        Returns:
            None
        """
        self._global_run_args[key] = val

    def set_run_args(self, keys: list, vals: list):
        """
        Set a list of `keys` to `vals

        .. note::
            List lengths must be the same

        Args:
            keys:
                list of keys to set
            vals:
                list of vals to set to

        Returns:
            None
        """
        keys = ensure_list(keys)
        vals = ensure_list(vals)

        if len(keys) != len(vals):
            raise ValueError(
                f"number of keys ({len(keys)}) != number of vals ({len(vals)}"
            )

        for key, val in zip(keys, vals):
            self._global_run_args[key] = val

    def update_run_args(self, d: dict):
        """
        Update current global run args with a dictionary `d`

        Args:
            d:
                dict of new args

        Returns:
            None
        """
        self._global_run_args.update(d)

    @property
    def do_not_recurse(self) -> bool:
        self._do_not_recurse = False
        return True

    @property
    def dependency(self) -> Dependency:
        return self._dependency

    @property
    def is_child(self) -> bool:
        if self.dependency is None:
            return False
        return self.short_uuid in self.dependency._children

    @property
    def is_parent(self) -> bool:
        if self.dependency is None:
            return False
        return self.short_uuid in self.dependency._parents

    def _mirror_dependency(self, dataset) -> None:
        self._logger.info(f"connecting with dataset {dataset}")
        if dataset.dependency is not None:
            self._logger.info("target has dependency, joining")
            self._dependency = dataset.dependency
        elif self.dependency is not None:
            self._logger.info("self has dependency, joining")
            dataset._dependency = self._dependency
        else:
            self._logger.info("creating a dependency and entering")
            self._dependency = Dependency()
            dataset._dependency = self.dependency

        self.database.update(self.pack())

    def set_downstream(self, dataset) -> None:
        self._mirror_dependency(dataset)

        self.dependency.add_edge(self, dataset)

        if not dataset.do_not_recurse:
            dataset._do_not_recurse = True
            dataset.set_upstream(self)

    def set_upstream(self, dataset) -> None:
        self._mirror_dependency(dataset)

        self.dependency.add_edge(dataset, self)

        if not dataset.do_not_recurse:
            dataset._do_not_recurse = True
            dataset.set_downstream(self)

    def pack(self, **kwargs) -> dict:
        """
        Override for the SendableMixin.pack() method, ensuring the dataset is
        always below a ``uuid``

        Args:
            **kwargs:
                Any arguments to be passed onwards to the SendableMixin.pack()

        Returns:
            (dict) packing result
        """
        if len(kwargs) == 0:
            self._logger.info("Dataset override pack called")
        else:
            self._logger.info("Data override pack called with run_args")
            self._logger.info(f"{format_iterable(kwargs)}")
        return super().pack(uuid=self._uuid, **kwargs)

    def update_db(self):
        self.database.update(self.pack())

    def set_run_option(self, key: str, val) -> None:
        """
        Update a global run option `key` with value `val`

        Args:
            key (str):
                option to be updated
            val:
                value to set
        """
        warnings.warn("set_run_option is deprecated, use set_run_arg instead")
        self._global_run_args[key] = val

    def append_run(
        self,
        args: dict = None,
        arguments: dict = None,
        name: str = None,
        extra_files_send: list = None,
        extra_files_recv: list = None,
        dependency_call: bool = False,
        verbose: int = None,
        quiet: bool = False,
        skip: bool = True,
        force: bool = False,
        lazy: bool = False,
        chain_run_args: bool = True,
        extra: str = None,
        return_runner: bool = False,
        **run_args,
    ):
        """
        Serialise arguments for later runner construction

        Args:
            args (dict):
                dictionary of arguments to be unpacked
            arguments (dict):
                alias for args
            name (str):
                 append a runner under this name
            extra_files_send (list, str):
                extra files to send with this run
            extra_files_recv (list, str):
                extra files to retrieve with this run
            dependency_call (bool):
                True if called via the dependency handler
            verbose (int, Verbose, None):
                verbose level for this runner (defaults to Dataset level)
            quiet (bool):
                disable printing for this append if True
            skip (bool):
                ignores checks for an existing runner if set to False
            force (bool):
                always appends if True
            lazy (bool):
                performs a "lazy" append if True, skipping the dataset update. You MUST
                call ds.finish_append() after you are done appending to avoid strange
                behaviours
            chain_run_args (bool):
                for dependency runs, will not propagate run_args to other datasets in
                the chain if False (defaults True)
            extra:
                extra string to add to this runner
            return_runner:
                returns the appened (or matching) runner if True
            run_args:
                any extra arguments to pass to runner
        """

        self._logger.debug("#### Dataset append_run called")
        Quiet.state = quiet
        if args is None and arguments is not None:
            args = arguments

        if verbose is None:
            verbose = self.verbose.value

        if self.dependency is not None and not dependency_call:
            return self.dependency.append_run(
                caller=self,
                chain_run_args=chain_run_args,
                args=args,
                name=name,
                extra_files_send=extra_files_send,  # noqa: E251
                extra_files_recv=extra_files_recv,  # noqa: E251
                verbose=verbose,
                quiet=quiet,
                skip=skip,
                force=force,
                lazy=lazy,
                run_args=run_args,
                extra=extra,
                return_runner=return_runner,
            )

        extra_files_send = ensure_list(extra_files_send) + self._extra_files["send"]
        extra_files_recv = ensure_list(extra_files_recv) + self._extra_files["recv"]

        rnum = len(self.runners)
        if name is not None:
            run_args["name"] = name
            r_id = name

            if name in self.runner_dict:
                self._logger.warning(
                    f"{self} overwriting already existing runner {r_id}"
                )
        else:
            r_id = f"runner-{rnum}"

        tmp = Runner(
            arguments=args,
            dbfile=self.dbfile,
            parent=self,
            self_id=r_id,
            extra_files_send=extra_files_send,
            extra_files_recv=extra_files_recv,
            verbose=verbose,
            extra=extra,
            **run_args,
        )

        tmp.result_extension = self.serialiser.extension

        tmp = self.insert_runner(tmp, skip, force, lazy, quiet, return_runner)

        if return_runner:
            return tmp

    def insert_runner(
        self,
        runner,
        skip: bool = True,
        force: bool = False,
        lazy: bool = False,
        quiet: bool = False,
        return_runner: bool = False,
    ):
        Quiet.state = quiet

        if runner.parent != self:
            self._logger.runtime(
                "inserting runner from another dataset, overriding parent"
            )

            runner._parent = self
            runner._parent_uuid = self.uuid

        def append_to_log(msg):
            session = f"append session {self._append_session}"

            try:
                self._append_log[session].append(msg)
            except KeyError:
                self._append_log[session] = [msg]

        r_id = runner.id

        if force or not skip:
            self._runs[r_id] = runner
            # regenerate a ``uuid`` so this runner can be properly tracked
            runner._generate_uuid({"r_id": r_id})

            self._uuids.append(runner.uuid)
            self._logger.important(f"force appended run {runner.name}", silent=lazy)
            append_to_log(f"force appended run {runner.name}")
        elif runner.uuid not in self._uuids:
            self._runs[r_id] = runner
            self._uuids.append(runner.uuid)
            self._logger.important(f"appended run {runner.name}", silent=lazy)
            append_to_log(f"append run {runner.name}")
        else:
            runner = self.get_runner(runner.uuid)
            self._logger.important(f"runner {runner.name} already exists", silent=lazy)
            append_to_log(f"skip append {runner.name}")

        if not lazy:
            self.finish_append(print_summary=False)
            Quiet.state = False

        if return_runner:
            return runner

    def finish_append(self, dependency_call: bool = False, print_summary: bool = True):
        if print_summary and len(self._append_log) != 0:
            self._append_session += 1
            append = 0
            force = 0
            skip = 0
            session = list(self._append_log.keys())[-1]
            for msg in self._append_log[session]:
                if msg.startswith("force"):
                    force += 1
                elif msg.startswith("append"):
                    append += 1
                elif msg.startswith("skip"):
                    skip += 1
            # condense the summary into a single line
            output = [f"Of {append + force + skip} appends: {append + force} added"]

            if force > 0:
                output.append(f" ({force} forced)")
            if skip > 0:
                output.append(f", {skip} skipped")

            output.append(". See run_log for more info")

            self._logger.important("".join(output))

        self._logger.info("finishing append")
        if self.dependency is not None and not dependency_call:
            return self.dependency.finish_append()

        self.database.update(self.pack())

    def lazy_append(self):
        return LazyAppend(self)

    def copy_runners(self, dataset):
        for runner in dataset.runners:
            self.insert_runner(runner, lazy=True, quiet=True)
        self.finish_append()

    @property
    def append_log(self):
        output = []

        for session in self._append_log:
            if len(self._append_log) <= 1:
                output = [f"{line}" for line in self._append_log[session]]
                break

            output.append(f"{session}:")

            output += [f"\t{line}" for line in self._append_log[session]]

        return "\n".join(output)

    def remove_run(self, id: any, dependency_call: bool = False) -> bool:
        """
        Remove a runner with the given identifier. Search methods are identical
        get_runner(id)

        Args:
            id:
                identifier
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion

        Returns:
            (bool): True if succeeded
        """
        if not dependency_call and self.dependency is not None:
            return self.dependency.remove_run(id)

        runner = self.get_runner(id, dependency_call)

        if runner is None:
            self._logger.info(f"could not find runner to remove")
            return False

        del self._runs[runner.id]
        self._uuids.remove(runner.uuid)

        self._logger.important(f"removed runner {runner}")

        # need to override attribute first, as updating can only add
        self.database._storage[self.uuid]["_runs"] = {}
        self.database.update(self.pack())

        return True

    def get_runner(self, id, dependency_call: bool = False) -> [Runner, None]:
        """
        Collect a runner with the given identifier. Depending on the type of
        arg passed, there are different search methods:

        - int: the runners[id] of the runner to remove
        - str: searches for a runner with the matching uuid
        - dict: attempts to find a runner with matching args

        Args:
            id:
                identifier
            dependency_call (bool):
                used by the dependencies, runners cannot be removed via uuid in this
                case, as the uuids will not match between datasets

        Returns:
            (Runner): collected Runner, None if not available
        """

        def get_by_id(id):
            self._logger.info(f"getting runner by id {id}")
            try:
                key = list(self.runner_dict.keys())[id]
                return self.runner_dict[key]
            except IndexError:
                return

        def get_by_str(id):
            self._logger.info(f'getting runner by string "{id}"')

            if id.lower() in self.runner_dict:
                return self.runner_dict[id.lower()]

            if dependency_call:
                raise RuntimeError(
                    "runners within a dependency cannot be removed by uuid"
                )
            # assume uuid at this point, search first by matching the first 8 chars
            # short_uuid, then confirming with the full, if given
            if len(id) == 64:
                self._logger.info(f"full uuid")
                for runner in self.runners:
                    if runner.uuid == id:
                        return runner
            elif len(id) == 8:
                self._logger.info(f"short uuid")
                for runner in self.runners:
                    if runner.short_uuid == id:
                        return runner

        def get_by_dict(id):
            self._logger.info(f"getting runner by args {id}")
            for r_id, r in self.runner_dict.items():
                if format_iterable(r.args) == format_iterable(id):
                    return r

        dispatch = {int: get_by_id, str: get_by_str, dict: get_by_dict}

        return dispatch.get(type(id))(id)

    def wipe_runs(self, dependency_call: bool = False) -> None:
        """
        Removes all runners

        Args:
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
        """
        if not dependency_call and self.dependency is not None:
            return self.dependency.clear_runs()

        self._logger.info("wiping all runners and updating the db")

        self._uuids = []
        self._runs = {}

        self.database._storage[self.uuid]["_runs"] = {}
        self.database.update(self.pack())

    def reset_runs(self, wipe: bool = True, dependency_call: bool = False) -> None:
        """
        Remove any results from the stored runners and attempt to delete their
        result files if `wipe=True`

        .. warning::
            This is a potentially destructive action, be careful with this
            method

        Args:
            wipe:
                Additionally deletes the local files if True. Default True
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion
        """
        if not dependency_call and self.dependency is not None:
            return self.dependency.clear_results(wipe)

        self._logger.runtime("clearing results")
        for runner in self.runners:
            runner.clear_result(wipe)

    def collect_files(
        self,
        remote_check: bool,
        results_only: bool = False,
        extra_files_send: bool = True,
    ) -> list:
        """
        Collect created files

        Args:
            remote_check:
                search for remote paths if True
            results_only:
                only collect files that are returned from a run such as Results and
                extra_files_recv if True
            extra_files_send:
                collects extra_files_send if True

        Returns:
            list of filepaths
        """
        target = "remote" if remote_check else "local"

        targets = []

        if not results_only:
            targets = [
                self.master_script.__getattribute__(target),
                self.repofile.__getattribute__(target),
            ]

        # grab all runner files
        for runner in self.runners:
            # start with constants
            targets += [
                runner.resultfile.__getattribute__(target),
                runner.errorfile.__getattribute__(target),
            ]
            # add the jobscript and runfile if we want all files
            if not results_only:
                targets += [
                    runner.jobscript.__getattribute__(target),
                    runner.runfile.__getattribute__(target),
                ]

            # need extra files, within their remote/local dir
            # also needs to be a copy of this list to prevent remote check contamination
            extras = [f for f in runner.extra_files_recv]
            if extra_files_send:
                for file in runner.extra_files_send:
                    extras.append(file)

            for file in extras:
                targets.append(file.__getattribute__(target))

        # minimize length
        targets = list(set(targets))

        return targets

    def wipe_local(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
    ) -> None:
        """
        Clear out the local directory

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion

        Returns:
            None
        """
        if not dependency_call and self.dependency is not None:
            return self.dependency.wipe_local(files_only)

        if not files_only and not check_dir_is_child(os.getcwd(), self.local_dir):
            raise RuntimeError(
                f"local dir {self.local_dir} is not a child directory, "
                f"deleting could have catastrophic effects"
            )

        self._logger.debug("wiping local")

        if not files_only:
            targets = [self.local_dir]
            for runner in self.runners:
                if runner.local_dir not in targets:
                    targets.append(runner.local_dir)

            self._logger.debug(f"locals: {format_iterable(targets)}")
            if dry_run:
                for local in targets:
                    print(f"targeting local {local} for wipe")

            for local in targets:
                try:
                    shutil.rmtree(local)
                    self._logger.debug(f"{local} removed")
                except FileNotFoundError:
                    self._logger.debug(f"{local} not found")

        else:
            self._logger.debug("file only wipe")
            targets = self.collect_files(remote_check=False, extra_files_send=False)

            self._logger.info(f"targets for wipe:|{format_iterable(targets)}")

            if dry_run:
                for local in targets:
                    print(f"targeting local {local} for wipe")

            for path in targets:
                try:
                    if "*" in path:
                        self._logger.debug(f"skipping wildcard: {path}")
                        continue
                    os.remove(path)
                    self._logger.debug(f"removed: {path}")
                except FileNotFoundError:
                    self._logger.debug(f"not found: {path}")

    def wipe_remote(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
    ) -> None:
        """
        Clear out the remote directory (including run dir)

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion

        Returns:
            None
        """
        self._logger.debug("wiping remote")

        if not dependency_call and self.dependency is not None:
            return self.dependency.wipe_remote(files_only)

        if not files_only:
            remotes = [self.remote_dir]
            for runner in self.runners:
                if runner.remote_dir not in remotes:
                    remotes.append(runner.remote_dir)
                if runner.run_path not in remotes:
                    remotes.append(runner.run_path)

            self._logger.debug(f"remotes: {format_iterable(remotes)}")
            if dry_run:
                for remote in remotes:
                    print(f"targeting remote {remote} for wipe")

            remotestr = ",".join(remotes)
            cmd = f"rm -rf {{{remotestr}}}"

            self.url.cmd(cmd)

        else:
            self._logger.debug("file only wipe")
            targets = self.collect_files(remote_check=True)

            self._logger.info(f"targets for wipe:|{format_iterable(targets)}")

            # skip any wildcards
            targets = [t for t in targets if "*" not in t]

            cmd = ",".join(targets)
            cmd = f"rm -rf {{{cmd}}}"

            if dry_run:
                for remote in targets:
                    print(f"targeting remote {remote} for wipe")
                return

            self.url.cmd(cmd)

    def hard_reset(
        self,
        files_only: bool = True,
        dry_run: bool = False,
        dependency_call: bool = False,
    ) -> None:
        """
        Hard reset the dataset, including wiping local and remote folders

        Args:
            files_only (bool):
                delete individual files instead of whole folders (preserves
                extra files)
            dry_run (bool):
                print targets and exit
            dependency_call (bool):
                used by any dependencies that exist, prevents recursion

        Returns:
            None
        """
        if not dependency_call and self.dependency is not None:
            return self.dependency.hard_reset(files_only)

        self.wipe_local(files_only, dry_run)
        self.wipe_remote(files_only, dry_run)
        self.wipe_runs()

        try:
            os.remove(self.dbfile)
        except FileNotFoundError:
            pass

    def backup(self, file=None, force: bool = False, full: bool = False):
        """
        Backs up the Dataset and any attached results/extra files to zip file

        Args:
            file:
                target path
            force:
                overwrite file if it exists
            full:
                also collect local files if True (defaults ``False``)
        Returns:
            path to zip file
        """
        if file is None:
            file = f"{self.name}.zip"

        if not file.endswith(".zip"):
            raise ValueError(f'backup file "{file}" must be of .zip type')

        file = os.path.abspath(file)

        if os.path.isfile(file) and not force:
            raise RuntimeError(
                f'backup file "{file}" exists, use a different name or '
                f"force=True to overwrite"
            )

        self._logger.debug(f"writing to file {file}")

        with open(Dataset._manifest_file, "w+", encoding="utf-8") as o:
            o.write(self.dbfile)

        with ZipFile(file, "w") as z:
            self._logger.runtime(f"storing file {self.database.path}")
            z.write(self.database.path)
            z.write(Dataset._manifest_file)

            rtn = not full  # if we're not collecting the full backup, only returns
            for rfile in self.collect_files(remote_check=False, results_only=rtn):
                if not os.path.isfile(rfile):
                    continue
                self._logger.runtime(f"storing file {rfile}")
                z.write(rfile)

        os.remove(Dataset._manifest_file)

        return file

    @classmethod
    def restore(cls, file, force: bool = False):
        """
        Restore from backup file `file`

        Args:
            file:
                File to restore from
            force:
                Set to True to overwrite any existing Dataset

        Returns:
            Dataset
        """
        # backup archive
        arch = ZipFile(file)
        # get the name of the Database file to recreate the Dataset
        with arch.open(name=Dataset._manifest_file, mode="r") as a:
            dbfile = a.read().decode("utf-8")
        if not force and os.path.exists(dbfile):
            raise RuntimeError(
                f"Dataset already exists, either restore with "
                f"force=True or delete the dbfile '{dbfile}'"
            )

        # extract all files that aren't the manifest
        files = [f for f in arch.namelist() if f is not Dataset._manifest_file]
        arch.extractall(members=files)
        # recreate and return
        dataset = Dataset.from_file(dbfile)

        return dataset

    @property
    def runner_dict(self) -> dict:
        """
        Stored runners in dict form, where the keys are the append id
        """
        return dict(self._runs)

    @property
    def runners(self) -> list:
        """
        Stored runners as a list
        """
        return list(self.runner_dict.values())

    @property
    def function(self) -> Function:
        """
        Currently stored Function wrapper
        """
        return self._function

    @property
    def extra(self):
        return self._global_run_extra

    @extra.setter
    def extra(self, extra):
        self._global_run_extra = extra

    @property
    def shebang(self) -> str:
        return self.url.shebang

    @shebang.setter
    def shebang(self, shebang: str):
        self.url.shebang = shebang

    def _script_sub(self, avoid_nodes: bool = False, **sub_args) -> str:
        """
        Substitutes run argmuents into the computer script, if it exists

        Args:
            avoid_nodes (bool):
                ignore submission scripts if True
            **sub_args:
                jobscript arguments

        Returns:
            (str):
                jobscript
        """
        default = f"{self.shebang}\n{self._script}"
        if avoid_nodes:
            self._logger.info("creating a jobscript for the login nodes")
            return default
        if not self._computer:
            self._logger.info("not a computer, returning base script")
            return default
        if "name" not in sub_args:
            self._logger.info(
                f"name not found in args, appending self name {self.name}"
            )
            sub_args["name"] = self.name
        return self.url.script(**sub_args)

    @property
    def script(self, **sub_args) -> str:
        """
        Currently stored run script

        Args:
            sub_args:
                arguments to substitute into the script() method

        Returns:
            (str):
                arg-substituted script
        """
        sub_args.update(self.run_args)
        return self._script_sub(**sub_args)

    @script.setter
    def script(self, script: str) -> None:
        """
        Set the run script
        """
        self._script = script

    @property
    def add_newline(self):
        return self._add_newline

    @add_newline.setter
    def add_newline(self, add_newline):
        self._add_newline = add_newline

    @property
    def submitter(self) -> str:
        """
        Currently stored submission command
        """
        return self.url.submitter

    @submitter.setter
    def submitter(self, submitter) -> None:
        """
        Set the submission command
        """
        self.url.submitter = submitter

    @property
    def url(self) -> URL:
        """
        Currently stored URL object
        """
        if not hasattr(self, "_url"):
            # noinspection PyTypeChecker
            self.url = None
        return self._url

    @url.setter
    def url(self, url: [URL, None] = None) -> None:
        """
        Verifies and sets the URL to be used.
        Will create an empty (local) url connection if url is None

        Args:
            url (URL):
                url to be verified
        """
        self._logger.info(f"new url is being set to {url}")
        if url is None:
            self._logger.info(
                "no URL specified for this dataset, creating " "localhost"
            )
            self._url = URL(verbose=self.verbose)
        else:
            if not isinstance(url, URL):
                raise ValueError("URL is not a valid URL instance")
            self._url = url

        if not type(url) == URL and issubclass(type(url), URL):  # noqa: E721
            self._computer = True

        timeout = self._global_run_args.get("timeout", None)
        max_timeouts = self._global_run_args.get("max_timeouts", None)

        self._url.timeout = timeout
        self._url.max_timeouts = max_timeouts

        try:
            self.transport.url = self.url
        except AttributeError:
            pass

    @property
    def transport(self) -> tp.transport.Transport:
        """
        Currently stored Transport system
        """
        if not hasattr(self, "_transport"):
            # noinspection PyTypeChecker
            self.transport = None
        return self._transport

    @transport.setter
    def transport(self, transport: [tp.transport.Transport, None] = None) -> None:
        """
        Verifies and sets the Transport to be used.
        Will use rsync if transport is None

        Args:
            transport (Transport):
                transport to be verified
        """
        if transport is None:
            self._logger.info(
                "no transport specified for this dataset, " "creating basic rsync"
            )
            self._transport = tp.rsync(self.url)
        else:
            if not isinstance(transport, tp.transport.Transport):
                raise ValueError("transport is not a valid transport instance")
            self._transport = transport
            self._transport.url = self.url

        self._transport.set_remote(self.url)

    @property
    def serialiser(self) -> sr.serial.serial:
        if not hasattr(self, "_serialiser"):
            self.serialiser = None
        return self._serialiser

    @serialiser.setter
    def serialiser(self, serialiser: sr.serial.serial = None) -> None:
        """
        Verifies and sets the serialiser to be used.
        Will use serialjson if serialiser is None

        Args:
            serialiser (serialiser):
                serialiser to be verified
        """
        if serialiser is None:
            self._logger.info("no serialiser specified," "creating basic json")
            self._serialiser = sr.serialjson()

        else:
            if not isinstance(serialiser, sr.serial.serial):
                raise ValueError("serialiser is not a valid serial instance")
            self._serialiser = serialiser

    @property
    def extra_files(self) -> dict:
        """
        Extra files to send and recieve
        """
        return self._extra_files

    def remove_database(self) -> None:
        """
        Deletes the database file
        """
        os.remove(self.dbfile)

    @property
    def name(self) -> str:
        """
        Name of this dataset
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets the dataset name
        """
        if not isinstance(name, str):
            raise ValueError(f"name {name} is not str type")

        self._name = name

    @property
    def uuid(self) -> str:
        """
        This Dataset's full uuid (64 characcter)
        """
        return self._uuid

    @property
    def short_uuid(self) -> str:
        """
        This Dataset's short format (8 character) uuid
        """
        return self._uuid[:8]

    def set_runner_states(
        self, state: str, uuids: list = None, extra: str = None
    ) -> None:
        """
        Update runner states to `state`

        Args:
            (str) state:
                state to set
            (list) uuids:
                list of uuids to update, updates all if not passed
        """
        self._logger.info("updating runner states")
        runners = []
        if uuids is not None:
            self._logger.info(f"using uuid list: {uuids}")
            for runner in self.runners:
                if runner.uuid in uuids:
                    runners.append(runner)
        else:
            runners = self.runners

        for runner in runners:
            runner.state = state

            if extra is not None:
                runner.state.extra = extra

    def get_all_runner_states(self) -> list:
        """
        Check all runner states, returning a list

        Returns (list):
            states
        """
        return [r.state for r in self.runners]

    def check_all_runner_states(self, state: str) -> bool:
        """
        Check all runner states against `state`, returning True if `all`
        runners have this state

        Args:
            state (str):
                state to check for

        Returns (bool):
            all(states)
        """
        return all([r == state for r in self.get_all_runner_states()])

    @property
    def last_run(self) -> [int, None]:
        """
        Returns the unix time of the last _run call

        Returns:
            (int): unix time of last  _run call, or None if impossible
        """
        if self._last_run > 0:
            return self._last_run
        return None

    @property
    def run_summary_limit(self):
        return self._run_summary_limit

    @run_summary_limit.setter
    def run_summary_limit(self, lim):
        self._run_summary_limit = lim

    def retry_failed(self, *args, **kwargs):
        kwargs["uuids"] = [r.uuid for r in self.failed]
        kwargs["force"] = True
        self.run(*args, **kwargs)

    def run(
        self,
        force: bool = False,
        dry_run: bool = False,
        quiet: bool = False,
        uuids: list = None,
        extra: str = "",
        force_ignores_success: bool = False,
        **run_args,
    ):
        """
        Run the functions

        Args:
            force (bool):
                force all runs to go through, ignoring checks
            dry_run (bool):
                create files, but do not run
            quiet (bool):
                suppress printing if True
            uuids (list):
                list of uuids to run
            extra:
                extra text to add to runner jobscripts
            failed_only (bool):
                If True, `force` will submit only failed runners
            force_ignores_success (bool):
                If True, `force` takes priority over `is_success` check
            run_args:
                any arguments to pass to the runners during this run.
                will override any "global" arguments set at Dataset init
        """
        self.avoid_runtime()
        runtime = int(time.time())
        self._logger.runtime(f"#### Dataset run called at {runtime}")
        self._last_run = runtime
        self._run_cmd = None
        self._run_log = []

        run_args["force"] = force

        Quiet.state = quiet

        if os.name == "nt" and self.url.is_local:
            raise RuntimeError(localwinerror)

        if self.dependency:
            self._logger.runtime(
                f"dataset {self} is a part of a dependency "
                f"chain, calling from there"
            )
            self.dependency.run(
                dry_run=dry_run,
                force_ignores_success=force_ignores_success,
                extra=extra,
                **run_args,
            )
            Quiet.state = False
            return

        if uuids is not None:
            self._logger.runtime(f"running only runners {format_iterable(uuids)}")

        # first step is to handle the writing of the scripts to the local dir
        # the runners take care of this
        runners_to_update = []
        master_content = ["sourcedir=$PWD"]
        goahead = False
        summary_only = len(self.runners) > self.run_summary_limit
        asynchronous = True  # should always be updated in the loop
        for runner in self.runners:
            if uuids is not None and runner.uuid not in uuids:
                self._logger.runtime(
                    f"Runner {runner} (uuid {runner.short_uuid}) is not in selection"
                )
                continue

            ready = runner.stage(
                python=self.url.python,
                global_extra=self.extra,
                extra=extra,
                summary_only=summary_only,
                force_ignores_success=force_ignores_success,
                **run_args,
            )

            if not ready:
                self._run_log.append(f"skipping runner {runner}")
                continue
            else:
                self._run_log.append(f"runner {runner} submitted")

            self.transport.queue_for_push(runner.jobscript)
            self.transport.queue_for_push(runner.runfile)
            # get our submitter
            if not runner.run_args.get("avoid_nodes", False):
                submitter = self.url.submitter
            else:
                submitter = self.url.shell
            # relpath to the jobscript
            jobscript = runner.jobscript.relative_remote_path(
                self.master_script.remote_dir
            )
            jobpath, jobfile = os.path.split(jobscript)
            # relpath to target error file
            errorpath = runner.errorfile.relative_remote_path(runner.remote_dir)
            runline = [
                f'sed -i -e "s#{runner.short_uuid}_master#$sourcedir#" {jobfile} &&'
            ]
            if runner.remote_dir != runner.run_path:
                runline.append(f"mkdir -p {runner.run_dir} &&")

            runline.append(f"{submitter} {jobfile} 2> {errorpath}")

            # get relative path to jobscript, but we must ``cd`` into it to stop any
            # run_dirs being created in the wrong remote
            if self.remote_dir != runner.remote_dir:
                runline.insert(0, f"cd {jobpath} && ")

            asynchronous = runner.run_args["asynchronous"]
            if asynchronous and submitter == "bash":
                self._logger.debug('appending "&" for async run')
                runline.append("&")

            self._logger.runtime("queuing extra files to send")
            for file in runner.extra_files_send:
                self.transport.queue_for_push(file)

            runners_to_update.append(runner.uuid)
            master_content.append(" ".join(runline))

            goahead = True

        if not goahead:
            self._logger.runtime("no runners completed the run assessment, skipping")

            return self._run_finalise(summary_only)

        if self.dependency is None:
            # next, we need the repository for the runners to import from
            self._write_to_repo()

            # master_content.insert(0, f"rm -f *{self.short_uuid}*error.out\n")
            self.master_script.write(master_content, add_newline=self.add_newline)

            self.transport.queue_for_push(self.master_script)

            launch_cmd = self.url.shell
            cmd = f"cd {self.remote_dir} && {launch_cmd} {self.master_script.name}"
            if not dry_run:
                self.transport.transfer()
                extra = None if not force else "forced"
                self.set_runner_states(
                    state="submit pending", uuids=runners_to_update, extra=extra
                )
                self._run_cmd = self.url.cmd(cmd, asynchronous=asynchronous)
            else:
                self.transport.wipe_transfers()
                self.set_runner_states("dry run", runners_to_update)
                self._logger.important(f"launch command: {cmd}")

        else:
            # if we are part of a dependency, just send the runner exclusive files
            self.transport.transfer()
            self.set_runner_states("submit pending", runners_to_update)

        self._run_finalise(summary_only)

    def _write_to_repo(self):
        if len(cached_functions) == 0:
            content = []
        else:
            content = [
                "### cached functions ###",
                *[f.source for f in cached_functions.values()],
            ]

        content += [
            "### primary function ###",
            self.function.source,
            "\n### serialiser functions ###",
            self.serialiser.dumpfunc(),
            self.serialiser.loadfunc(),
        ]

        self.repofile.write(content)

        self.transport.queue_for_push(self.repofile)

    def _run_finalise(self, summary_only: bool = False) -> None:
        if summary_only:
            run = 0
            skip = 0
            force = 0
            for runner in self.runners:
                if runner._run_state == "skip":
                    skip += 1
                elif runner._run_state == "run":
                    run += 1
                elif runner._run_state == "force":
                    run += 1
                    force += 1
            # condense the summary into a single line
            output = [f"Of {len(self.runners)} runners, {run} run,"]

            if force > 0:
                output.append(f"({force} forced)")
            if skip > 0:
                output.append(f"({skip} skipped)")

            output.append("see run_log for more info")

            self._logger.important(" ".join(output))

        self.database.update(self.pack())
        Quiet.state = False

    @property
    def run_log(self):
        return "\n".join(self._run_log)

    @property
    def run_cmd(self) -> CMD:
        """
        Access to the storage of CMD objects used to run the scripts

        Returns:
            (list): List of CMD objects
        """
        return self._run_cmd

    def check_runner_outputs(self):
        # check the files of the runners not reporting as completed
        # files to check
        resultfiles = []
        errorfiles = []
        extrafiles = []
        for runner in self.runners:
            if runner.state == "reset":
                self._logger.info("runner is in a reset state, ignoring")
                continue
            resultfiles.append(runner.resultfile.remote)
            errorfiles.append(runner.errorfile.remote)

            extrafiles += [f.remote for f in runner.extra_files_recv]

        self._logger.runtime("checking remotely for runner outputs")
        search, _ = self.url.utils._file_mtime(
            resultfiles + errorfiles + extrafiles,
            local=self.url.is_local,
            python=False,
            dry_run=False,
        )

        # separate out the error files into their own dict
        errors = {}
        extras = {}
        for file in errorfiles:
            try:
                errors[file] = search.pop(file)
            except KeyError:
                pass

        for file in extrafiles:
            try:
                extras[file] = search.pop(file)
            except KeyError:
                pass

        for runner in self.runners:
            ls = runner.last_submitted
            self._logger.info(f"checking against last submitted {ls}")

            if ls == 0:
                self._logger.info("runner has not been run")
                continue

            if runner.resultfile.remote in search:
                t, s = search[runner.resultfile.remote]
                self._logger.info(f"found resultfile (t={t}, size={s})", end="... ")

                if ls > t:
                    # outdated file, ignore
                    self._logger.info("outdated")
                else:
                    self._logger.info("looks good")
                    runner.resultfile.confirm_remote(t)
                    runner.resultfile.size = s
            else:
                self._logger.info("no result found")

            if runner.errorfile.remote in errors:
                t, s = errors[runner.errorfile.remote]
                self._logger.info(f"found errorfile (t={t}, size={s})", end="... ")

                if ls > t:
                    # outdated file, ignore
                    self._logger.info("outdated")
                else:
                    self._logger.info("looks good")
                    runner.errorfile.confirm_remote(t)
                    runner.errorfile.size = s
            else:
                self._logger.info("no errors found")

        return search, errors, extras

    @property
    def is_finished(self):
        return self._is_finished()

    def _is_finished(self):
        self.avoid_runtime()
        t = int(time.time())
        self._logger.runtime(f"#### _is_finished called at {t}")
        fin = {r.uuid: r.is_finished for r in self.runners}

        if all([r.is_success for r in self.runners]):
            self._logger.runtime("all runners are marked Succeeded, returning early")
            return list(fin.values())

        self._logger.runtime("runners polled, checking for files")
        search, errors, extras = self.check_runner_outputs()

        # parse runner states
        for runner in self.runners:
            if runner.is_success:
                self._logger.runtime(
                    f"runner {runner} is already marked as completed successfully"
                )
                continue
            elif fin[runner.uuid] is None:
                self._logger.runtime(f"runner {runner} has not been submitted")
                continue
            # final check and status updates
            ls = runner.last_submitted

            tmp_fin = False
            if runner.resultfile.last_seen_remote >= ls:
                self._logger.runtime("valid result found, reporting as completed")
                runner.state = "completed"
                tmp_fin = True
            else:
                if runner.errorfile.last_seen_remote >= ls:
                    self._logger.runtime("found a valid error file", end="... ")

                    if runner.errorfile.size == 0:
                        self._logger.runtime("empty")
                        runner.state = "submitted"
                    else:
                        self._logger.runtime("has content")
                        runner.state = "failed"
                        tmp_fin = True

            fin[runner.uuid] = tmp_fin

        self._logger.runtime(f"runner states: |{format_iterable(fin)}")
        return list(fin.values())

    @property
    def all_finished(self) -> bool:
        """
        Check if `all` runners have finished

        Returns (bool):
            True if all runners have completed their runs
        """
        return all(self.is_finished)

    @property
    def all_success(self) -> bool:
        self._is_finished()
        return all([r.is_success for r in self.runners])

    def wait(
        self,
        interval: int = 10,
        timeout: int = None,
        watch: bool = False,
        success_only: bool = False,
    ) -> None:
        """
        Watch the calculation, printing updates as runners complete

        Args:
            interval:
                check interval time in seconds
            timeout:
                maximum time to wait in seconds
            watch:
                print an updating table of runner states
            success_only:
                Completion search ignores failed runs if True

        Returns:
            None
        """

        def wait_condition():
            if success_only:
                return self.all_success

            states = self._is_finished()
            return all([s for s in states if s is not None])

        if watch:
            from IPython.display import clear_output

        t0 = time.time()

        # check all non None states
        while not wait_condition():
            if watch:
                # noinspection PyUnboundLocalVariable
                clear_output(wait=True)
                print(
                    f"watching {len(self.runners)} runners, with a {interval}s interval"
                )

                if timeout:
                    print(f"will time out if t > {timeout}")

            dt = time.time() - t0

            if watch:
                print(f"t={dt:.2f}")

                for runner in self.runners:
                    statetxt = runner.state
                    print(f"{runner.name}, {statetxt}")

            if timeout is not None and dt > timeout:
                raise RuntimeError("wait timed out")

            time.sleep(interval)

    def fetch_results(
        self, results: bool = True, errors: bool = True, extras: bool = True
    ):
        """
        Fetch results from the remote, and store them in the runner results property

        Args:
            results:
                fetch result files
            errors:
                fetch error files
            extras:
                fetch extra files
        Returns:
            None
        """
        self.avoid_runtime()
        t = int(time.time())
        self._logger.runtime(f"#### fetch_results called at {t}")

        # if we're going to rely on runner states, we should update them
        self._is_finished()

        transfer = False
        for runner in self.runners:
            if runner.state == "satisfied":
                if not runner.verify_local_files():
                    self._logger.runtime(
                        "runner resultfile is missing locally, attempting a pull"
                    )
                    self.transport.queue_for_pull(runner.resultfile)
                    for file in runner.extra_files_recv:
                        self.transport.queue_for_pull(file)
                    transfer = True
                else:
                    self._logger.runtime("runner is satisfied, no work needed")

            elif runner.state == "completed":
                transfer = True
                if results:
                    self._logger.info("runner marked as completed, pulling result")
                    self.transport.queue_for_pull(runner.resultfile)
                else:
                    self._logger.info("runner marked as completed, but ignoring result")

                if runner.errorfile.size != 0:
                    # There can be an error and result, so we should pull both
                    if errors:
                        self.transport.queue_for_pull(runner.errorfile)

                if extras:
                    for file in runner.extra_files_recv:
                        self.transport.queue_for_pull(file)

            elif runner.state == "failed":
                transfer = True
                self._logger.info("runner marked as completed, pulling error")
                if errors:
                    self.transport.queue_for_pull(runner.errorfile)

        if transfer:
            self._logger.runtime("a transfer was requested, transfer and read")
            self.transport.transfer(raise_errors=False)

            for cmd in self.transport.cmds:
                if cmd.stderr:
                    warnings.warn(
                        f"\nWARNING! When transferring files, "
                        f"fetch_results encountered an error:\n{cmd.stderr}"
                    )

            for runner in self.runners:
                runner.read_local_files()

        self.update_db()

    def fetch_errors(self):
        """
        Fetch only error files from remote

        Returns:
            None
        """
        self.fetch_results(results=False, errors=True, extras=False)

    @property
    def results(self) -> list:
        """
        Access the results of the runners

        Returns (list):
            ``runner.result`` for each runner
        """
        self.avoid_runtime()
        self._logger.runtime("#### Dataset results called")
        # check first for errors
        n_errors = len([e for e in self.errors if e is not None])
        if n_errors != 0:
            self._logger.warning(
                f"Warning! Found {n_errors} error(s), "
                f"also check the `errors` property!"
            )
        return [r.result for r in self.runners]

    @property
    def errors(self) -> list:
        """
        Access the errors of the runners

        Returns (list):
            ``runner.error`` for each runner
        """
        self.avoid_runtime()
        self._logger.runtime("#### Dataset errors called")
        return [r.error for r in self.runners]

    @property
    def failed(self) -> list:
        """
        Returns a list of failed runners

        Returns:
            list of failed runners
        """
        return [r for r in self.runners if r.state.failed]

    def avoid_runtime(self) -> None:
        """
        Call for last_runtime sensitive operations such as is_finished and fetch_results

        Waits for 1s if we're too close to the saved _last_run time

        Returns:
            None
        """
        checktime = int(time.time())

        if checktime <= self._last_run:
            self._logger.runtime("call is too soon after last run, sleeping for 1s")
            time.sleep(1)
