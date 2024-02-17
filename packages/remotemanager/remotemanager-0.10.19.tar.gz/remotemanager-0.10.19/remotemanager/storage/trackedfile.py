import time

from remotemanager.storage.sendablemixin import SendableMixin
from remotemanager.utils import dir_delta

import os


class TrackedFile(SendableMixin):
    __slots__ = ["_remote_path", "_local_path", "_file", "_last_seen", "_size"]

    def __init__(self, local_path: str, remote_path: str, file: str):
        self._remote_path = remote_path
        self._local_path = local_path
        self._file = file

        self._last_seen = {"remote": -1, "local": -1}
        self._size = -1

    def __repr__(self):
        return self.local

    def __fspath__(self):
        return self.name

    @property
    def name(self):
        return self._file

    @property
    def importstr(self):
        return os.path.splitext(self._file)[0]

    @property
    def remote(self):
        return os.path.join(self._remote_path, self.name)

    @property
    def local(self):
        return os.path.join(self._local_path, self.name)

    @property
    def remote_dir(self):
        return self._remote_path

    @property
    def local_dir(self):
        return self._local_path

    def relative_remote_path(self, other: str) -> str:
        """
        Return a path relative to `cwd`

        Args:
            other:
                working dir to compare against

        Returns:
            relative path
        """
        # if our remote path is an abspath, we already have what we need
        if os.path.isabs(self.remote_dir):
            return self.remote

        # we're already in the remote, just return the filename
        if self.remote_dir == other:
            return self.name

        # find the deepest shared path, treat it as a "root"
        stem = os.path.commonpath([self.remote_dir, other])
        # find how far down this stem is from `other`
        dirdelta = dir_delta(stem, other)
        # generate a ../ string that steps "down" to the common path
        down = "../" * dirdelta

        tmp_remote = self.remote_dir.replace(stem, "").strip("/")
        # rebuild up from our virtual root
        return os.path.join(down, tmp_remote, self.name)

    @property
    def content(self):
        if not os.path.isfile(self.local):
            return None
        with open(self.local, "r") as o:
            self.confirm_local()
            return o.read()

    def _write(self, content, append, add_newline):
        if not os.path.isdir(self.local_dir):
            os.makedirs(self.local_dir)
        # try to join lists, falling back on a basic str coercion
        if not isinstance(content, str):
            try:
                content = "\n".join(content)
            except TypeError:
                content = str(content)

        if append:
            mode = "a+"
        else:
            mode = "w+"

        with open(self.local, mode) as o:
            o.write(content)

            if add_newline and not content.endswith("\n"):
                o.write("\n")

        self.confirm_local()

    def write(self, content: (str, list), add_newline: bool = True) -> None:
        """
        Write `content` to the local copy of the file

        Args:
            content:
                content to write
            add_newline:
                enforces a newline character at the end of the write if True
                (default True)
        Returns:
            None
        """
        self._write(content, append=False, add_newline=add_newline)

    def append(self, content: str, add_newline: bool = True) -> None:
        """
        Append `content` to the local copy of the file

        Args:
            content:
                content to append
            add_newline:
                enforces a newline character at the end of the write if True
                (default True)
        Returns:
            None
        """
        self._write(content, append=True, add_newline=add_newline)

    def confirm_local(self, t: int = None):
        """
        Confirm sighting of the file locally
        """
        if t is None:
            t = int(time.time())
        self._last_seen["local"] = t

    def confirm_remote(self, t: int = None):
        """
        Confirm sighting of the file on the remote
        """
        if t is None:
            t = int(time.time())
        self._last_seen["remote"] = t

    @property
    def exists_local(self):
        """Returns True if the file exists locally"""
        return os.path.exists(self.local)

    def last_seen(self, where: str) -> int:
        return self._last_seen[where]

    @property
    def last_seen_local(self):
        return self.last_seen("local")

    @property
    def last_seen_remote(self):
        return self.last_seen("remote")

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
