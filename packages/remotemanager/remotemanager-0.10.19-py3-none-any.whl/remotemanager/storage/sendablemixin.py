import collections.abc
import importlib
import json
import logging
import os.path
from collections import deque

import yaml

INTERNAL_STORAGE_KEYS = {
    "CLASS_STORAGE_KEY": "~serialisedclass~",
    "TUPLE_STORAGE_KEY": "~serialisedtuple~",
    "SET_STORAGE_KEY": "~serialisedset~",
    "DEQUE_STORAGE_KEY": "~serialiseddeque~",
    "SERIALISED_STORAGE_KEY": "~serialisedobject~",
    "SLOTS_ENABLE_KEY": "~usesslots~",
}

_logger = logging.getLogger(__name__)


class SendableMixin:
    """
    Mixin class to create "sendable" object.
    Provides methods for conversion to yaml format

    Create a sendable object by subclassing SendableMixin at class creation

    >>> class MyObject(SendableMixin):
    >>>     ...

    Instances of this object will now have the required methods to be
    converted to and from dict format

    >>> new = MyObject()
    >>> payload = new.pack()  # store the object in a dict object
    >>> recreated = MyObject.unpack(payload)  # create an instance from dict
    """

    __slots__ = ["_unpack_validate"]
    serialiser = NotImplemented

    def pack(self, uuid: str = None, file: str = None) -> [dict, None]:
        """
        "packs" the object into a dict-format, ready for yaml-dump

        Args:
            uuid (str):
                Optional uuid string to package this data inside.
                Adds a toplevel `uuid` to the payload dict:
                >>> p = {...}

                Becomes:
                >>> p = {uuid: {...}}

            file (str):
                Directly package to file with `yaml.dump`

        Returns:
            (dict):
                object payload
        """
        # remove any attributes not to be packaged
        # these objects are either not needed, or can be re-created on the
        # recipient end
        never_package = ["_logger", "_logobj"]
        class_storage = get_class_storage(self)

        # if the object is a subclass, find the name of the parent by getting
        # the mro of the object, and extracting it from the set
        # parent_class_names = get_mro_classnames(self)

        # if the class specifies a solo _do_not_package, add that
        never_package += getattr(self.__class__, "_do_not_package", [])

        payload = {}
        if hasattr(self, "__dict__"):
            # print("standard pack")
            for k, v in self.__dict__.items():
                if k in never_package:
                    # print(f"skipping k = {k}")
                    payload[k] = {
                        INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"]: {
                            "mod": "remotemanager.storage.sendablemixin",
                            "name": "Unloaded",
                        }
                    }
                    continue

                payload[self.serialise(k)] = self.serialise(v)
        else:
            # print("slots pack")
            payload[INTERNAL_STORAGE_KEYS["SLOTS_ENABLE_KEY"]] = True
            for key in self.__slots__:
                payload[self.serialise(key)] = self.__getattribute__(key)

        payload[INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"]] = class_storage

        if uuid:
            if "_uuid" in payload and payload["_uuid"] != uuid:
                raise ValueError("passed uuid and _uuid key in payload do not match!")

            payload["_uuid"] = uuid

            payload = {uuid: payload}

        if file is not None:
            print(f"dumping payload to {file}")
            with open(file, "w+") as o:
                yaml.dump(payload, o)

            return None

        return payload

    @classmethod
    def unpack(cls, data: dict = None, file: str = None, limit: bool = True):
        """
        Re-create an object from a packaged payload coming from ``obj.pack``

        .. note ::
            use this function to unpack from a payload _outside_ an object

            .. code:: python

                newobj = MyObject.unpack(payload)

            Where ``MyObject`` is a subclass of SendableMixin,
            and ``payload`` is a dict-type coming from ``MyObject.pack()``

        Args:
            data (dict):
                __dict__ payload from the object that was packaged
            file (str):
                filepath to unpack from, if data is not given
            limit (bool):
                set False to allow outside classes to be unserialised

        Returns:
            re-created object
        """

        if data is None:
            if file is None:
                raise ValueError(
                    "please provide a data payload or filepath to read from"
                )
            elif not os.path.isfile(file):
                raise FileNotFoundError(f"could not find file {file}")

            with open(file, "r") as o:
                data = yaml.safe_load(o)

        # if the data passed is a {uuid: {data}} format dict, search for a ``uuid``
        # within and extract the {data}
        try:
            firstkey = list(data)[0]
            if (
                isinstance(data[firstkey], dict)
                and "_uuid" in data[firstkey]
                and data[firstkey]["_uuid"] == firstkey
            ):
                data = data[firstkey]
        except IndexError:
            # if there's no keys in data, then we definitely don't have a ``uuid``
            pass

        # create a new instance of this class
        new = cls.__new__(cls)

        # this is REQUIRED to be separate to the return call
        new.inject_payload(data, limit)

        return new

    def inject_payload(self, payload: dict, limit: bool = True):
        """
        inject payload into the __dict__, effectively re-creating the object

        .. note ::
            use this function to unpack _within_ an object

            >>> class MyObject(SendableMixin):
            >>>     def __init__(self, ...):
            >>>         ...
            >>>         self.inject_payload(payload)

        Args:
            payload (dict):
                __dict__ payload from the object that was packaged
            limit (bool):
                enable or disable safeties
        """
        if isinstance(self, Unloaded):
            return

        if hasattr(self, "_logger"):
            self._logger.info(f"finalising unpacking of {type(self)}")

        # temporary attribute to check for a valid class
        self._unpack_validate = True

        if INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"] in payload:
            selfkey = get_class_storage(self)
            packkey = payload[INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"]]

            if selfkey != packkey:
                raise RuntimeError(
                    f"attempting to unpack class "
                    f'{packkey["name"]} as '
                    f'{selfkey["name"]}'
                )

            delattr(self, "_unpack_validate")

        for k, v in payload.items():
            if k in list(INTERNAL_STORAGE_KEYS.values()):
                continue
            self.__setattr__(k, self.unserialise(v, limit))

    def serialise(self, obj):
        """
        Recurse over any iterable objects, or call the pack() method of any
        `SendableMixin` objects, for serialisation

        Args:
            obj:
                object to be packaged

        Returns (yaml-serialisable object):
            yaml-friendly object
        """

        if issubclass(type(obj), SendableMixin):
            payload = obj.pack()
            return payload

        elif isinstance(obj, collections.abc.Mapping):
            # dict type
            try:
                payload = {self.serialise(k): self.serialise(v) for k, v in obj.items()}
                return payload
            except TypeError as e:
                raise ValueError(
                    "Possible dictionary as key. These cause "
                    f"circular issues with YAML\nOriginal error: "
                    f"{e}"
                )

        elif isinstance(obj, list):
            # list-type
            return [self.serialise(v) for v in obj]

        elif isinstance(obj, tuple):
            # tuple-type
            return [INTERNAL_STORAGE_KEYS["TUPLE_STORAGE_KEY"]] + [
                self.serialise(v) for v in obj
            ]

        elif isinstance(obj, set):
            # set-type
            return [INTERNAL_STORAGE_KEYS["SET_STORAGE_KEY"]] + [
                self.serialise(v) for v in obj
            ]

        elif isinstance(obj, deque):
            # collections deque
            return [INTERNAL_STORAGE_KEYS["DEQUE_STORAGE_KEY"], obj.maxlen] + [
                self.serialise(v) for v in obj
            ]

        if basic_available(obj):
            return obj

        try:
            return [
                INTERNAL_STORAGE_KEYS["SERIALISED_STORAGE_KEY"],
                self.serialiser.dumps(obj),
            ]
        except AttributeError:
            pass

        raise RuntimeError(f"Failed to yaml dump {obj.__class__.__name__} object {obj}")

    def unserialise(self, obj, limit: bool = True):
        """
        Undo a serialised packaging, by importing the called object and calling
        its unpack() method

        Args:
            obj:
                payload to be unpacked
            limit (bool):
                exit if the object to be unpacked is not part of the
                remotemanager package

        Returns:
            object before packaging
        """
        try:
            unpackable = obj.get(INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"])
        except AttributeError:
            unpackable = False

        if unpackable:
            # extract the class to import
            source = obj.pop(INTERNAL_STORAGE_KEYS["CLASS_STORAGE_KEY"])

            if "_conn" in obj:
                # disable protection for URLs
                limit = False

            # import the module
            modulename = source["mod"]
            if limit and not modulename.startswith("remotemanager"):
                raise ValueError(
                    "module to import is not within the "
                    "remotemanager package, exiting for safety"
                )
            mod = importlib.import_module(modulename)

            # now get the actual class to import and unpack
            cls = getattr(mod, source["name"])

            return cls.unpack(obj)

        elif isinstance(obj, collections.abc.Mapping):
            # dict type
            return {self.unserialise(k): self.unserialise(v) for k, v in obj.items()}

        # coming from the yaml file, output should _only_ be list
        elif isinstance(obj, list):
            try:
                if obj[0] == INTERNAL_STORAGE_KEYS["TUPLE_STORAGE_KEY"]:
                    return tuple([self.unserialise(o) for o in obj[1:]])
                elif obj[0] == INTERNAL_STORAGE_KEYS["SET_STORAGE_KEY"]:
                    return set([self.unserialise(o) for o in obj[1:]])
                elif obj[0] == INTERNAL_STORAGE_KEYS["DEQUE_STORAGE_KEY"]:
                    maxlen = obj[1]
                    dqobj = obj[2:]
                    return deque([self.unserialise(o) for o in dqobj], maxlen=maxlen)
                else:
                    return [self.unserialise(v) for v in obj]
            except IndexError:
                return [self.unserialise(v) for v in obj]

        if basic_available(obj):
            return obj

        return obj

    def is_missing(self, objname: str) -> bool:
        """
        Determine if object with name objname is missing or uninitialised

        Args:
            objname (str): name of the object to look for

        Returns:
            (bool): object presence
        """

        if not hasattr(self, objname):
            return True

        obj = getattr(self, objname)
        if isinstance(obj, Unloaded):
            return True

        if obj is None:
            return True

        return False


class Unloaded(SendableMixin):
    def __init__(self):
        pass

    def __getattr__(self, item):
        pass


def get_class_storage(obj) -> dict:
    """
    Breaks down object into its module and classname.

    Args:
        obj:
            Python object to be broken down

    Returns (dict):
        module and classname dict
    """
    return {"mod": obj.__module__, "name": obj.__class__.__name__}


def get_mro_classnames(obj) -> list:
    return [subobj.__name__ for subobj in obj.__class__.__mro__]


def basic_available(obj):
    # attempt a base json serialisation, which will fail fast if we can't dump
    try:
        json.dumps(obj)
        return True
    except Exception as E:
        if hasattr(obj, "_logger"):
            obj._logger.error(str(E))
        return False
