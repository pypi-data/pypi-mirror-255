"""
URL base class for connecting to remote systems
"""
import logging
import os
import time
import typing
from collections import deque

from remotemanager.connection.testing_object import ConnectionTest
from remotemanager.logging.utils import format_iterable
from remotemanager.connection.cmd import CMD
from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.utils import ensure_list
from remotemanager.logging import LoggingMixin
from remotemanager.logging.verbosity import Verbosity


class URL(SendableMixin, LoggingMixin):
    """
    Container to store the url info for a Remote run

    The url should contain everything pertaining to the _remote_, allowing
    Dataset to be remote-agnostic

    Arguments:
        host (str):
            host address of the remote system
        user (str):
            username for the remote system
        port (int, str):
            port to connect to for ssh tunnels
        verbose (bool):
            base-verbosity for connections
        timeout (int):
            time to wait before issuing a timeout for cmd calls
        max_timeouts (int):
            number of times to attempt cmd communication in case of a timeout
        python (str):
            string used to initiate a python instance
        raise_errors (bool):
            set false to ignore errors by default in cmd calls
        passfile (str):
            absolute path to password file for sshpass calls
        envpass (str):
            environment variable containing absolute path to password file for
        sshpass_override (str):
            override the sshpass string
            sshpass calls
        cmd_history_depth (int):
            number of cmd calls to store history for
        landing_dir (str):
            set the directory which is treated as the ssh endpoint
        ssh_insert (str):
            any extra flags you wish to add to the ssh call
        quiet_ssh (bool):
            Option to add -q flag to ssh calls. This suppresses errors and warnings
            that machines can sometimes put on stderr, breaking runs. Defaults True
        kwargs:
            any extra args that may end up here from a Dataset or Computer are
            discarded
    """

    _localhost = "localhost"

    _do_not_package = ["_urlutils"]

    _defaults = {"python": "python", "submitter": "bash", "shell": "bash"}

    def __init__(
        self,
        host: str = None,
        user: str = None,
        port: int = None,
        verbose: [int, Verbosity] = None,
        timeout: int = 5,
        max_timeouts: int = 3,
        python: str = None,
        submitter: str = None,
        shell: str = None,
        raise_errors: bool = True,
        keyfile: str = None,
        passfile: str = None,
        envpass: str = None,
        sshpass_override: str = None,
        cmd_history_depth: int = 10,
        landing_dir: str = None,
        ssh_insert: str = "",
        quiet_ssh: bool = True,
        shebang: str = "#!/bin/bash",
        **kwargs,
    ):
        self._verbose = Verbosity(verbose)

        if host is None:
            if user is not None:
                raise ValueError(
                    f"user is set to {user}, but host is unset, "
                    f'did you mean to set host="{user}"?'
                )

            host = URL._localhost
        elif "@" in host and user is None:
            user, host = host.split("@")

        self._conn = {"user": user, "host": host, "port": port}

        self.timeout = timeout
        self.max_timeouts = max_timeouts
        self._python = python
        self._submitter = submitter
        self._shell = shell
        self._shebang = shebang

        self._home = None
        self._landing_override = landing_dir

        self._cmd_history_depth = cmd_history_depth
        self._cmd_history = deque(maxlen=self._cmd_history_depth)
        # explicit path takes precedent over environment variable
        if passfile is None and envpass is not None:
            passfile = os.environ[envpass]

        if "ignore_errors" in kwargs:
            raise_errors = not kwargs.pop("ignore_errors")

        self._keyfile = keyfile
        self._passfile = passfile
        self._passfile_override = sshpass_override

        self._raise_errors = raise_errors
        self._ssh_override = None
        self._ssh_prepend = None
        self._ssh_insert = ssh_insert
        self.quiet_ssh = quiet_ssh

        self._logger.info(
            f"new url created with url details:{format_iterable(self._conn)}"
        )

        self._callcount = 0

        self._latency = 0
        self._connection_test = None

    @property
    def raise_errors(self):
        return self._raise_errors

    @raise_errors.setter
    def raise_errors(self, r):
        self._raise_errors = r

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
    def call_count(self) -> int:
        return self._callcount

    @property
    def user(self) -> str:
        """
        Currently configured username
        """
        return self._conn["user"]

    @user.setter
    def user(self, user):
        """
        Set the user attribute
        """
        self._conn["user"] = user

    @property
    def host(self) -> str:
        """
        Currently configured hostname
        """
        return self._conn["host"] or URL._localhost

    @host.setter
    def host(self, host):
        """
        Set the host attribute
        """
        self._conn["host"] = host

    @property
    def userhost(self) -> str:
        """
        `user@host` string if possible, just `host` if user is not present
        """
        if self.user is None:
            return self.host
        else:
            return f"{self.user}@{self.host}"

    @property
    def shebang(self) -> str:
        return self._shebang

    @shebang.setter
    def shebang(self, shebang: str):
        self._shebang = shebang

    @property
    def ssh_insert(self) -> str:
        return self._ssh_insert

    @ssh_insert.setter
    def ssh_insert(self, val: str):
        self._ssh_insert = val

    @property
    def ssh_prepend(self) -> str:
        return self._ssh_prepend

    @ssh_prepend.setter
    def ssh_prepend(self, val: str):
        self._ssh_prepend = val

    @property
    def python(self):
        if self._python is not None:
            return self._python
        return URL._defaults["python"]

    @python.setter
    def python(self, python):
        self._python = python

    @property
    def submitter(self):
        if self._submitter is not None:
            return self._submitter
        if self._shell is not None:
            self._logger.debug("submitter is None but shell is set, returning shell")
            return self._shell
        return URL._defaults["submitter"]

    @submitter.setter
    def submitter(self, submitter):
        self._submitter = submitter

    @property
    def shell(self):
        if self._shell is not None:
            return self._shell
        return URL._defaults["shell"]

    @shell.setter
    def shell(self, shell):
        self._shell = shell

    @property
    def port(self) -> int:
        """
        Currently configured port (defaults to 22)
        """
        port = self._conn["port"] or 22
        return port

    @property
    def home(self) -> str:
        if self._home is None:
            self.gethome()
        return self._home

    def gethome(self):
        self._home = self.expandvars("$HOME")

    def clearhome(self):
        """
        Clear the home property

        Returns:
            None
        """
        self._home = None

    @property
    def landing_dir(self):
        if self._landing_override is not None:
            return self._landing_override

        if self.home is not None:
            return self.home

        self._logger.debug("fallback to returning $HOME")
        return "$HOME"

    @landing_dir.setter
    def landing_dir(self, landing):
        self._logger.info(f"updating landing dir to {landing}")
        self._landing_override = landing

    @property
    def ssh(self) -> str:
        """
        ssh insert for commands on this connection
        """
        if self.is_local:
            return ""

        if self._ssh_override:
            return self._ssh_override

        ret = []

        if self.passfile is not None:
            ret.append(self.passfile)

        if self.ssh_insert != "":
            ret.append(f"ssh {self.ssh_insert} -p {self.port}")
        else:
            ret.append(f"ssh -p {self.port}")

        if self.quiet_ssh:
            ret.append("-q")

        if self._keyfile:
            ret.append(f"-i {self.keyfile}")

        ret.append(self.userhost)

        return " ".join(ret)

    @ssh.setter
    def ssh(self, newssh: str) -> None:
        """
        Allows forced override of the ssh command

        Inserting extra flags into the ssh can be done as follows:

        >>> url = URL()
        >>> print(url.ssh)
        >>> "ssh"
        >>> url.ssh = "LANG=C " + url.ssh
        >>> print(url.ssh)
        >>> "LANG=C ssh"

        Args:
            newssh (str):
                new ssh string to insert

        Returns:
            None
        """
        self._ssh_override = newssh

    def clear_ssh_override(self):
        """
        Wipe any override applied to ssh. Can also be done by setting
        url.ssh = None

        Returns:
            None
        """
        self._ssh_override = None

    @property
    def keyfile(self):
        if self._keyfile is None:
            return
        p = self._keyfile.replace("~", os.environ["HOME"])
        if not os.path.isfile(p):
            raise RuntimeError(f"could not find ssh key file at {self._keyfile}")

        return self._keyfile

    @keyfile.setter
    def keyfile(self, file):
        self._keyfile = file

    @property
    def passfile(self) -> [str, None]:
        """
        Returns the sshpass string

        .. versionadded:: 0.10.2
            No longer returns just the file, to facilitate overriding

        Returns:
            sshpass full string
        """
        if self._passfile_override is not None:
            return self._passfile_override

        if self._passfile is None:
            return

        p = self._passfile.replace("~", os.environ["HOME"])
        if not os.path.isfile(p):
            raise RuntimeError(f"could not find password file at {self._passfile}")

        return f"sshpass -f {self._passfile}"

    @passfile.setter
    def passfile(self, file):
        self._passfile = file

    @property
    def is_tunnel(self):
        """
        Uses the presence of an assigned port to determine if we are tunnelling
        or not

        Returns (bool):
           True if this is a tunnelled connection
        """
        return self._conn["port"] is not None

    @property
    def is_local(self):
        """
        True if this connection is purely local
        """
        host = self.host
        if host == URL._localhost:
            return True
        elif host.startswith("127."):
            return True
        return False

    def ping(self, n: int = 5, timeout: int = 30) -> float:
        """
        Perform and monitor a ping command

        Args:
            n (int): number of pings to aim for
            timeout (int): kill the process and return 0 if
                this period is elapsed

        Returns:
            (float) latency in ms
        """
        self._logger.runtime(f"pinging {self.host}")

        def cleanup(process):
            process.kill()
            try:
                os.remove("tmp_ping")
                self._logger.debug("removed temporary file")
            except FileNotFoundError:
                self._logger.debug("temporary ping file could not be found")

        ping = self.cmd(
            f"ping {self.host}", local=True, stdout="tmp_ping", asynchronous=True
        )

        lines = []
        t0 = time.time()
        while len(lines) < n + 1:
            with open("tmp_ping", "r") as o:
                lines = o.readlines()

            time.sleep(0.5)

            if time.time() - t0 > timeout:
                self._logger.warning(f"ping timed out after {timeout} seconds")
                cleanup(ping)
                return -1

        cleanup(ping)

        times = []
        for line in lines[1:]:
            times.append(self._process_ping_line(line))

        avg = sum(times) / n
        self._logger.runtime(f"ping times: {times} -> {avg}")
        return avg

    def _process_ping_line(self, line: str) -> float:
        """
        Function to parse the contents of a line output from a ping command

        Args:
            line (str):
                ping command line
        Returns:
            (float): ping time in seconds
        """
        timing = line.split("time=")[1].strip()  # get timing
        val, units = timing.split()
        self._logger.debug(f"parsed line {line} -> {val} ({units})")

        if units != "ms":
            raise ValueError(f"Unknown ping units {units}")

        return float(val) * 1e-3  # convert to seconds

    def expandvars(self, string: str) -> str:
        """
        'echo' a string on the remote, returning the result

        Args:
            string:
                string to be expanded

        Returns:
            str
        """
        wrapped = f'bash -c "echo {string}"'

        return self.cmd(wrapped).stdout

    def cmd(
        self,
        cmd: str,
        asynchronous: bool = False,
        local: [bool, None] = None,
        stdout: str = None,
        stderr: str = None,
        timeout: int = None,
        max_timeouts: int = None,
        raise_errors: bool = None,
        dry_run: bool = False,
        prepend: bool = False,
        force_file: bool = False,
        landing_dir: str = None,
    ) -> typing.Union[CMD, str]:
        """
        Creates and executes a command

        Args:
            asynchronous (bool):
                run this command asynchronously
            cmd (str):
                command to execute
            local (bool, None):
                force a local or remote execution. Defaults to None
            stdout (str):
                optional file to redirect stdout to
            stderr (str):
                optional file to redirect stderr to
            timeout (int):
                time to wait before issuing a timeout
            max_timeouts (int):
                number of times to attempt communication in case of a timeout
            raise_errors (bool):
                override for global setting. Raise any stderr if encountered
            dry_run (bool):
                don't exec the command if True, just returns the string
            prepend (bool):
                always attempt to use ssh_prepend
            force_file (bool):
                passthrough for CMD force_file argument
            landing_dir:
                set the directory which is treated as the ssh endpoint

        Returns (CMD):
            returned command instance
        """
        _remote_call = False
        if self._landing_override is not None or landing_dir is not None:
            ld = landing_dir or self.landing_dir
            self._logger.debug(f"modifying cmd with landing dir {ld}")
            cmd = f"cd {ld} && {cmd}"

        if local is not None and not local:
            self._logger.info("forced remote call; appending ssh to cmd")
            cmd = f"{self.ssh} '{cmd}'"
            _remote_call = True
        elif local is None and not self.is_local:
            self._logger.info("implicit remote call; appending ssh to cmd")
            cmd = f"{self.ssh} '{cmd}'"
            _remote_call = True
        if raise_errors is None:
            raise_errors = self._raise_errors

        timeout = self.timeout if timeout is None else timeout
        max_timeouts = self.max_timeouts if max_timeouts is None else max_timeouts

        if self.ssh_prepend is not None:
            self._logger.info(f"found prepend string {self.ssh_prepend}")
            prep = self.ssh_prepend.strip()

            if prepend:
                self._logger.debug(f"force adding prepend string {prep}")
                cmd = f"{prep} {cmd}"
            elif _remote_call:
                self._logger.debug(f"implicit adding prepend string {prep}")
                cmd = f"{prep} {cmd}"

        if dry_run:
            return cmd.strip()

        thiscmd = CMD(
            cmd.strip(),
            asynchronous=asynchronous,
            stdout=stdout,
            stderr=stderr,
            timeout=timeout,
            max_timeouts=max_timeouts,
            raise_errors=raise_errors,
            force_file=force_file,
        )
        thiscmd.exec()
        if not local:
            self._callcount += 1

        self._cmd_history.append(thiscmd)

        return thiscmd

    @property
    def cmd_history(self):
        return self._cmd_history

    @property
    def cmd_history_depth(self):
        return self._cmd_history_depth

    @cmd_history_depth.setter
    def cmd_history_depth(self, newdepth: int):
        """
        Updates the history depth, and creates a new dequeue populated with as many of
        the existing cmds as possible

        Args:
            newdepth (int):
                new depth to capture
        Returns:

        """
        self._logger.info(
            f"updating history depth from {self.cmd_history_depth} to {newdepth}"
        )
        self._cmd_history_depth = newdepth

        newqueue = deque(maxlen=self.cmd_history_depth)

        for item in self.cmd_history:
            newqueue.append(item)

        self._cmd_history = newqueue

    @property
    def utils(self):
        """
        Handle for the URLUtils module
        """
        if self.is_missing("_urlutils"):
            self._urlutils = URLUtils(self)
        return self._urlutils

    def test_connection(self) -> None:
        """
        Create a ConnectionTest instance and run the tests

        Returns:
            None
        """
        testing_object = ConnectionTest(self)
        testing_object.exec()

        self._connection_test = testing_object

    @property
    def connection_test(self) -> ConnectionTest:
        """
        Return the connection test object

        Returns:
            ConnectionTest: testing object
        """
        return self._connection_test

    @property
    def connection_data(self) -> dict:
        """
        Returns the results of a previous connection test

        Returns:
            (dict) connection data
        """
        return self._connection_test.data

    @property
    def latency(self) -> [float, None]:
        """
        Attempts to access the latency property of the stored ConnectionTest

        Returns:
            (float): connection latency in seconds, if available. Else None
        """
        if self._connection_test is not None:
            return self._connection_test.latency
        return None

    def script(self, **kwargs):
        raise NotImplementedError


class URLUtils:
    """
    Extra functions to go with the URL class, called via URL.utils

    As it requires a parent `URL` to function, and is instantiated with a
    `URL`, there is little to no purpose to using this class exclusively

    Arguments:
        parent (URL):
            parent class to provide utils to
    """

    def __init__(self, parent: URL):
        self._logger = logging.getLogger(__name__ + ".URLUtils")
        self._logger.info(f"creating a utils extension to parent: {parent}")

        self._parent = parent

    def file_mtime(
        self,
        files: list,
        local: bool = None,
        python: bool = False,
        ignore_empty: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """
        Check file modification times of [files]

        Args:
            files (list):
                list of paths to files
            local (bool):
                force a local search
            python (bool):
                ensure python style search is used
            ignore_empty (bool):
                also check the filesize, ignoring empty files
            dry_run (bool):
                print command only

        Returns (dict):
            {file: mtime (unix)} dictionary
        """

        self._logger.info(f"performing stat on files: {files}")
        if local is None:
            local = self._parent.is_local

        files = ensure_list(files)
        times, error = self._file_mtime(files, local, python, dry_run)

        if dry_run:
            # in this instance "times" is simply the command
            return times

        self._logger.info("received:")
        self._logger.info(times)
        self._logger.info(error)
        output = {}
        for file in files:
            if file in times:
                mtime = times[file][0]
                fsize = times[file][1]
                if ignore_empty and fsize == 0:
                    output[file] = None
                else:
                    output[file] = mtime
            else:
                output[file] = None

        return output

    def _file_mtime(self, files: list, local: bool, python: bool, dry_run: bool):
        """
        Perform the "stat -c %Y" command on a list of files,
        returning the result. Uses a python command backup if this fails

        Args:
            files (list):
                list of files to check
            local (bool):
                force a local search
            python (bool):
                force the python override
            dry_run (bool):
                print command only

        Returns:
            (list): list of file unix times
        """
        sep = ","

        def stat():
            self._logger.debug("attempting raw stat command on files")
            basecmd = f"stat -c %n{sep}%Y{sep}%s"
            if len(files) == 1:
                cmd = f"{basecmd} {files[0]}"
            else:
                cmd = f"{basecmd} {{" + ",".join(files) + "}"

            ret = self._parent.cmd(
                cmd, local=local, raise_errors=False, dry_run=dry_run
            )

            if dry_run:
                return ret, "", "", ""

            times = {}
            for line in ret.stdout.split("\n"):
                try:
                    fname = line.split(sep)[0]
                    mtime = int(float(line.split(sep)[1]))
                    fsize = int(float(line.split(sep)[2]))

                    times[fname] = (mtime, fsize)
                except IndexError:
                    pass

            return times, ret.stderr.split("\n"), ret.returncode, ret.stderr

        def pystat():
            self._logger.debug("attempting python stat on files")
            ex = f"""import os
files={files}
for f in files:
\ttry: print(f'{{f}}{sep}{{os.stat(f).st_mtime}}{sep}{{os.stat(f).st_size}}')
\texcept FileNotFoundError: print(f)"""

            cmd = f'{self._parent.python} -c "{ex}"'

            ret = self._parent.cmd(
                cmd, local=local, raise_errors=False, dry_run=dry_run
            )

            if dry_run:
                return ret, None

            times = {}
            error = []
            for line in ret.stdout.split("\n"):
                try:
                    fname = line.split(sep)[0]
                    mtime = int(float(line.split(sep)[1]))
                    fsize = int(float(line.split(sep)[2]))

                    times[fname] = (mtime, fsize)
                except IndexError:
                    error.append(line.strip())

            return times, error

        files = ensure_list(files)

        if not python:
            t, e, returncode, stderr = stat()
            if returncode in [126, 127] or "illegal option" in stderr:
                self._logger.warning("stat failed, falling back on python")
                return pystat()

            return t, e

        return pystat()

    def file_presence(
        self, files: list, local: bool = None, dry_run: bool = False
    ) -> dict:
        """
        Search for a list of files, returning a boolean presence dict

        Args:
            files (list):
                list of paths to files
            local (bool):
                force a local search
            dry_run (bool):
                print command only

        Returns (dict):
            {file: present} dictionary
        """
        self._logger.info(f"checking for presence of files: {files}")
        if local is None:
            local = self._parent.is_local

        files = ensure_list(files)

        times = self.file_mtime(files, local=local, dry_run=dry_run)

        if dry_run:
            return times

        return {f: times[f] is not None for f in files}

    def search_folder(
        self, files: list, folder: str, local: bool = None, dry_run: bool = False
    ) -> dict:
        """
        Search `folder` for `files`, returning a boolean presence dict

        Arguments:
            files (list):
                list of filenames to check for. Optionally, a string for a
                single file
            folder (str):
                folder to scan
            local (bool):
                perform the scan locally (or remotely)
            dry_run (bool):
                print command only

        Returns (dict):
            {file: present} dictionary
        """
        if local is None:
            local = self._parent.is_local
        fpath = os.path.abspath(folder) if local else folder

        self._logger.debug(f"scanning folder {fpath}")
        self._logger.debug("searching for files:")
        self._logger.debug(f"{format_iterable(files)}")

        ls_return = self.ls(fpath, local=local, as_list=True, dry_run=dry_run)

        if dry_run:
            self._logger.info("dry run, returning command")
            return ls_return

        scan = [os.path.basename(f) for f in ls_return]

        self._logger.debug("scan sees:")
        self._logger.debug(f"{format_iterable(scan)}")

        if isinstance(files, str):
            self._logger.info("files is a string, running in singular mode")
            ret = {files: os.path.basename(files) in scan}
        else:
            ret = {file: os.path.basename(file) in scan for file in files}

        return ret

    def touch(
        self,
        file: str,
        local: bool = None,
        raise_errors: bool = None,
        dry_run: bool = False,
    ) -> CMD:
        """
        perform unix `touch`, creating or updating `file`

        Arguments:
            file (str):
                filename or path to file
            local (bool):
                force local (or remote) execution
            raise_errors (bool):
                raise any stderr encountered
            dry_run (bool):
                print command only

        Returns (CMD):
            CMD instance for the command
        """
        if local is None:
            local = self._parent.is_local
        self._logger.debug(f"utils touch on file {file}")
        fname = os.path.abspath(file) if local else file
        return self._parent.cmd(
            f"touch {fname}", local=local, raise_errors=raise_errors, dry_run=dry_run
        )

    def mkdir(
        self,
        file: str,
        local: bool = None,
        raise_errors: bool = None,
        dry_run: bool = False,
    ) -> CMD:
        """
        perform unix `mkdir -p`, creating a folder structure

        Arguments:
            file (str):
                name or path to folder
            local (bool):
                force local (or remote) execution
            raise_errors (bool):
                raise any stderr encountered
            dry_run (bool):
                print command only

        Returns (CMD):
            CMD instance for the command
        """
        if local is None:
            local = self._parent.is_local
        self._logger.debug(f"utils mkdir on path {file}")
        fname = os.path.abspath(file) if local else file
        return self._parent.cmd(
            f"mkdir -p {fname}", local=local, raise_errors=raise_errors, dry_run=dry_run
        )

    def ls(
        self,
        file: str,
        as_list: bool = True,
        local: bool = None,
        raise_errors: bool = None,
        dry_run: bool = False,
    ) -> [CMD, list]:
        """
        Identify the files present on the directory

        Arguments:
            file (str):
                name or path to folder.
            as_list (bool):
                convert to a list format
            local (bool):
                force local (or remote) execution
            raise_errors (bool):
                raise any stderr encountered
            dry_run (bool):
                print command only

        Returns (CMD, list):
            CMD instance for the command, or the list if as_list is True
        """
        if local is None:
            local = self._parent.is_local
        self._logger.debug(f"utils ls on path {file}")
        fname = os.path.abspath(file) if local else file

        ret = self._parent.cmd(
            f"ls {fname}", local=local, raise_errors=raise_errors, dry_run=dry_run
        )

        if as_list and not dry_run:
            ret = [f for f in ret.stdout.split("\n") if f != ""]
        return ret
