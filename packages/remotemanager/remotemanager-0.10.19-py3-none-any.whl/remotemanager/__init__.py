from .dataset.dataset import Dataset
from .connection.url import URL
from .connection.computers.base import BaseComputer
from .logging.log import Handler
from .storage.remotefunction import RemoteFunction
from remotemanager.decorators.sanzufunction import SanzuFunction

__all__ = [
    "Dataset",
    "URL",
    "RemoteFunction",
    "BaseComputer",
    "SanzuFunction",
]  # noqa: F405
__version__ = "0.10.19"

# attach a global Logger to the manager
Logger = Handler()  # noqa: F405


# ipython magic
def load_ipython_extension(ipython):
    from remotemanager.decorators.magic import RCell

    ipython.register_magics(RCell)
