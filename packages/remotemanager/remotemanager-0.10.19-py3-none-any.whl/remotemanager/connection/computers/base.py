import json
import typing

import yaml

from typing import Union

from remotemanager.connection.url import URL
from remotemanager.connection.computers.options import optional, required, runargs
from remotemanager.storage.function import Function


def format_time(time: Union[int, str]) -> str:
    """
    Take integer seconds and generate a HH:MM:SS timestring

    Args:
        time (int):
            seconds
    Returns:
        (str):
            HH:MM:SS format timestamp
    """
    if not isinstance(time, int):
        # if given a string, assume format is already valid and return
        return time
    mins = time // 60
    hours = mins // 60

    secstring = str(time % 60).rjust(2, "0")
    minstring = str(mins % 60).rjust(2, "0")
    hourstring = str(hours).rjust(2, "0")

    return f"{hourstring}:{minstring}:{secstring}"


def time_to_s(time: str) -> int:
    """Convert back from HH:MM:SS to integer seconds"""
    hh, mm, ss = 0
    hh, mm, ss = time.split(":")

    return int(hh) * 3600 + int(mm) * 60 + int(ss)


class BaseComputer(URL):
    """
    Base computer module for HPC connection management.

    Extend this class for connecting to your machine
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._parser = None

        self.choice_groupings = []

        self._extra = ""
        self._internal_extra = ""

    def __setattr__(self, key, value):
        """
        If the set `key` attribute is an MPI option, instead set the `value`
        of that attribute

        Args:
            key:
                attribute name to set
            value:
                value to set to

        Returns:
            None
        """
        if key in self.__dict__:
            if isinstance(getattr(self, key), (optional, required)):
                getattr(self, key).value = value
                return

        object.__setattr__(self, key, value)

    def pack(self, *args, **kwargs):
        if not isinstance(self._parser, (Function, type(None))):
            self._parser = Function(self._parser)

        return super().pack(*args, **kwargs)

    @classmethod
    def from_dict(cls, spec: dict, **url_args):
        """
        Create a Computer class from a `spec` dictionary. The required values are:

        - resources:
            a dict of required resources for the machine (mpi, nodes, queue, etc.)
        - resource_parser:
            a function which takes a dictionary of {resource: Option}, returning a list
            of valid jobscript lines

        You can also provide some optional arguments:

        - required_or:
            list of resources, ONE of which is required. Note that this must be a
            _list_ of dicts, one for each or "block"
        - optional_resources:
            as with `resources`, but these will not be stored as required values
        - optional_defaults:
            provide defaults for the names given in optional_resources. When adding the
            optional arg, the optional_defaults will be checked to see if a default is
            provided
        - host:
            machine hostname. Note that this _must_ be available for a job run, but if
            not provided within the spec, can be added later with
            ``url.host = 'hostname'``
        - submitter:
            override the default submitter
        - python:
            override the default python
        - extra:
            any extra lines that should be appended after the resource specification.
            Note that this includes module loads/swaps, but this can be specified on a
            per-job basis, rather than locking it into the `Computer`

        The `resources` specification is in `notebook`:`machine` order. That is to say
        that the `key` is what will be required in the _notebook_, and the `value` is
        what is placed in the jobscript:

        >>> spec = {'resources': {'mpi': 'ntasks'}, ...}
        >>> url = BaseComputer.from_dict(spec)
        >>> url.mpi = 12
        >>> url.script()
        >>> "--ntasks=12"

        Args:
            spec (dict):
                input dictionary
            url_args:
                any arguments to be passed directly to the created `url`

        Returns:
            Computer class as per input spec
        """
        from remotemanager import Logger

        def set_resource_spec(field, flag, opt=False, default=None) -> None:
            """
            Set the resource requester in the computer

            Args:
                field:
                    name under which to apply
                flag:
                    placeholder arguments
                opt:
                    True if optional argument. Required as default can be None
                default:
                    default arg (if any)
            """
            if isinstance(flag, str):
                args = {"flag": flag}

            else:
                args = flag

            if opt:
                args["default"] = default
                attribute = optional(**args)
            elif "default" in args:
                attribute = optional(**args)
            else:
                attribute = required(**args)

            computer.__setattr__(field, attribute)

        # create a new class
        computer = cls()

        # convert the parser back into a function
        parser_source = spec.pop("resource_parser_source", None)
        if parser_source is not None:
            Logger.debug("generating parser from source code")
            computer.parser = Function(parser_source)
        else:  # legacy unpack method
            Logger.debug("parser source code not found at resource_parser_source")
            parser_source = spec.pop("resource_parser")
            if isinstance(parser_source, str):
                Logger.debug("discovered string at resource_parser, treating")
                computer.parser = Function(parser_source)
            elif isinstance(parser_source, dict):
                Logger.debug(f"dict found, unpacking into Function")
                computer.parser = Function.unpack(parser_source)
            else:
                Logger.debug(
                    f"no string found, setting {type(parser_source)} "
                    f"{parser_source} as parser"
                )
                computer.parser = parser_source

        # add the resource storing objects to the class
        required_resources = spec.pop("resources")
        selected_resources = spec.pop("required_or", [])
        optional_resources = spec.pop("optional_resources", {})

        for field, flag in required_resources.items():
            set_resource_spec(field, flag, opt=False)

        for group in selected_resources:
            allnames = list(group)
            computer.choice_groupings.append(allnames)

            for field, flag in group.items():
                set_resource_spec(field, flag, opt=False)

        defaults = spec.pop("optional_defaults", {})
        for field, flag in optional_resources.items():
            default = None
            if field in defaults:
                default = defaults[field]
            set_resource_spec(field, flag, opt=True, default=default)

        # add any extra content
        for key, val in spec.items():
            computer.__setattr__(key, val)

        for key, val in url_args.items():
            computer.__setattr__(key, val)

        return computer

    def to_dict(self) -> dict:
        """
        Generate a spec dict from this Computer

        Returns:
            dict
        """

        def create_entry(obj):
            data = {"flag": obj.flag}

            if obj.min is not None:
                data["min"] = obj.min
            if obj.max is not None:
                data["max"] = obj.max
            if getattr(obj, "default", None) is not None:
                data["default"] = obj.default

            return data

        spec = {}

        if self.host:
            spec["host"] = self.host

        spec["shebang"] = getattr(self, "shebang", "#!/bin/bash")
        spec["extra"] = getattr(self, "extra", "")
        spec["submitter"] = getattr(self, "submitter", "bash")

        required = {}
        required_or = []
        optional = {}
        defaults = {}

        flat = []
        for group in self.choice_groupings:
            tmp = {}
            for name in group:
                flat.append(name)
                obj = getattr(self, name)
                tmp[name] = create_entry(obj)

            required_or.append(tmp)

        for name in self.arguments:
            if name in flat:
                continue
            obj = getattr(self, name)
            if name in self.required:
                required[name] = create_entry(obj)
            else:
                optional[name] = create_entry(obj)

                if obj.default:
                    defaults[name] = obj.default

        spec["resources"] = required

        if len(required_or) > 0:
            spec["required_or"] = required_or

        if len(optional) > 0:
            spec["optional_resources"] = optional

        if len(defaults) > 0:
            spec["optional_defaults"] = defaults

        # avoids a strange error where the parser source cant be found.
        # likely loads it into memory where `inspect` can access it
        # noinspection PyStatementEffect
        self.parser
        if isinstance(self._parser, Function):
            spec["resource_parser_source"] = self._parser.raw_source
        else:
            spec["resource_parser_source"] = Function(self.parser).raw_source

        return spec

    @classmethod
    def from_yaml(cls, filepath: str, **url_args):
        """
        Create a Computer from `filepath`.

        Args:
            filepath:
                path containing yaml computer spec
            **url_args:
                extra args to be passed to the internal URL

        Returns:
            BaseComputer
        """
        if isinstance(filepath, str):
            try:
                with open(filepath, "r") as o:
                    data = yaml.safe_load(o)
            except OSError:
                data = yaml.safe_load(filepath)
        else:
            data = yaml.safe_load(filepath)

        return cls.from_dict(data, **url_args)

    def to_yaml(self, filepath: Union[str, typing.IO, None] = None) -> Union[str, None]:
        """
        Dump a computer to yaml `filepath`.

        Args:
            filepath:
                path containing yaml computer spec
        """
        data = self.to_dict()
        # source will simply not print correctly with base yaml
        # extract it and do it manually
        parser_string = ["resource_parser_source: |"] + [
            f"    {line}" for line in data.pop("resource_parser_source").split("\n")
        ]
        # dump the remaining content to string
        prepared = yaml.dump(data)
        # append the cleaned string
        prepared += "\n".join(parser_string)

        if filepath is None:  # "dump" to string
            return prepared
        elif isinstance(filepath, str):  # dump to path
            with open(filepath, "w+") as o:
                o.write(prepared)
        else:  # assume file handler and dump there
            filepath.write(prepared)

    @classmethod
    def from_repo(
        cls,
        name: str,
        branch: str = "main",
        repo: str = "https://gitlab.com/l_sim/remotemanager-computers/",
        **url_args,
    ):
        """
        Attempt to access the remote-computers repo, and pull the computer with name
        `name`

        Args:
            name (str):
                computer name to target
            branch (str):
                repo branch (defaults to main)
            repo (str):
                repo web address (defaults to main l_sim repo)

        Returns:
            BaseComputer instance
        """
        import requests
        from remotemanager.utils import ensure_filetype

        def download_file(file_url, filename):
            response = requests.get(file_url)

            if response.status_code == requests.codes.ok:
                # Save the file
                with open(filename, "wb") as file:
                    file.write(response.content)
                print(f"Grabbed file '{filename}'")
            else:
                raise RuntimeError(f"Could not find a file at: {file_url}")

        filename = ensure_filetype(name, "yaml").lower()
        url = f"{repo}-/raw/{branch}/storage/{filename}"

        print(f"polling url {url}")

        download_file(url, filename)

        return cls.from_yaml(filename, **url_args)

    def generate_cell(
        self, name: Union[str, None] = None, return_string: bool = False
    ) -> None:
        """
        Prints out copyable source which regenerates this Computer

        Args:
            name (str, None):
                Optional name for new computer. Defaults to `new`
            return_string (bool):
                Also returns the string if True. Defaults to False

        Returns:
            (None, str)
        """
        if name is None:
            name = "new"
        output = [
            "# Copy the following into a jupyter cell or python script "
            "to generate a modifiable source",
            "\n# Parser source code",
        ]

        parser = self._parser
        if not isinstance(parser, Function):
            parser = Function(parser)

        output.append(parser.raw_source)

        output.append("\n# Spec dict")
        source = self.to_dict()
        source.pop("resource_parser_source")
        # use json.dumps with indent=4 to format dict
        output.append(f"spec = {json.dumps(source, indent=4)}")
        output.append(f'spec["resource_parser"] = {parser.name}')

        output.append(f"\n{name} = BaseComputer.from_dict(spec)")

        output = "\n".join(output)

        print(output)

        if return_string:
            return output

    @property
    def parser(self):
        if self._parser is None:
            return None
        if not isinstance(self._parser, Function):
            self._parser = Function(self._parser)
        return self._parser.object

    @parser.setter
    def parser(self, parser):
        if not isinstance(parser, Function):
            parser = Function(parser)
        self._parser = parser

    @property
    def arguments(self):
        return [
            k for k, v in self.__dict__.items() if isinstance(v, (optional, required))
        ]

    @property
    def argument_dict(self):
        return {k.strip(): getattr(self, k) for k in self.arguments}

    @property
    def required(self):
        """

        Returns the required arguments
        """
        return [k for k, v in self.__dict__.items() if isinstance(v, required)]

    @property
    def missing(self):
        """
        Returns the currently missing arguments
        """
        missing = [k for k in self.required if not getattr(self, k)]

        # check the groupings to make sure we're not raising any false positives
        for group in self.choice_groupings:
            if any(name not in missing for name in group):
                # at least one of the names in the group is present in the computer,
                # so we're fine to continue
                for name in group:
                    try:
                        missing.pop(missing.index(name))
                    except ValueError:
                        pass

        return missing

    @property
    def valid(self):
        return len(self.missing) == 0

    def update_resources(self, **kwargs):
        """
        Set any arguments passed to the script call

        Args:
            **kwargs:
                kwarg updates e.g. mpi=128
        Returns:
            None
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def resources_block(self, **kwargs):
        self.update_resources(**kwargs)

        if not self.valid:
            raise RuntimeError(f"missing required arguments: {self.missing}")

        if self._parser is None:
            return []

        submit_args = self.argument_dict
        submit_args["run_args"] = runargs(kwargs)

        return self.parser(submit_args)

    @property
    def extra(self):
        return self._internal_extra + self._extra

    @extra.setter
    def extra(self, external):
        self._extra = external

    def script(self, **kwargs) -> str:
        """
        Takes job arguments and produces a valid jobscript

        Returns:
            (str):
                script
        """
        script = [self.shebang]

        script += self.resources_block(**kwargs)

        if self.extra is not None:
            script += [self.extra]

        return "\n".join(script)
