import hashlib

from remotemanager.logging.utils import format_iterable


def generate_uuid(string: str) -> str:
    if not isinstance(string, str):
        string = format_iterable(string)
    h = hashlib.sha256()
    h.update(bytes(string, "utf-8"))

    return str(h.hexdigest())
