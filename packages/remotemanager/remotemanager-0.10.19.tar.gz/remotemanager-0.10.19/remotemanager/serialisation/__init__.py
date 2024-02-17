from remotemanager.serialisation.serialyaml import serialyaml
from remotemanager.serialisation.serialjson import serialjson
import remotemanager.serialisation.serial  # noqa: F401, this silences an IDE warning

__all__ = ["serialyaml", "serialjson"]

try:
    from remotemanager.serialisation.serialdill import serialdill  # noqa: F401

    __all__.append("serialdill")
except ImportError:
    pass

try:
    from remotemanager.serialisation.serialjsonpickle import (  # noqa: F401
        serialjsonpickle,
    )

    __all__.append("serialjsonpickle")
except ImportError:
    pass
