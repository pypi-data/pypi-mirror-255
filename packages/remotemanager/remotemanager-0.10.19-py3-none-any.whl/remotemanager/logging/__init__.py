import logging
from remotemanager.logging.quiet import Quiet


class LoggingMixin:
    _logobj = None

    @property
    def _logger(self):
        def create_logger():
            self._logobj = LoggerInsert(f"{__name__}.{self.__class__.__name__}", self)

        if self._logobj is not None:
            create_logger()

        if not isinstance(self._logobj, LoggerInsert):
            create_logger()
        return self._logobj


class LoggerInsert:
    """
    This class inserts itself between the logging Logger and the
    _logobj used
    """

    def __init__(self, logger: str, parent):
        self._logger = logging.getLogger(logger)

        self._add_logging_level("RUNTIME", 15)
        self._add_logging_level("IMPORTANT", 25)

        self._parent = parent

    def _add_logging_level(self, name, level):
        def loglevel(self, message, *args, **kwargs):
            if self.isEnabledFor(level):
                self._log(level, message, args, **kwargs)

        def logroot(message, *args, **kwargs):
            logging.log(level, message, *args, **kwargs)

        logging.addLevelName(level, name)
        setattr(logging, name.lower(), level)
        setattr(logging.getLoggerClass(), name.lower(), loglevel)
        setattr(logging, name.lower(), logroot)

    @property
    def verbose(self):
        try:
            return self._parent._verbose
        except AttributeError:
            return None

    def _print(self, msg, lvl, end):
        # print(f'\t{msg[:10]} @ {lvl}, quiet: {Quiet}')
        if Quiet:
            return
        try:
            self.verbose.print(msg, lvl, end)
        except AttributeError:
            # usually raised if the stored _verbose is None
            pass

    def add_uuid(self, msg):
        if hasattr(self._parent, "short_uuid"):
            return f"({self._parent.short_uuid}) {msg}"
        return msg

    def debug(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.debug(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 1, end=end)

    def runtime(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.runtime(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 2, end=end)

    def info(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.info(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 3, end=end)

    def important(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.important(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 4, end=end)

    def warning(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.warning(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 5, end=end)

    def error(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.error(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 6, end=end)

    def critical(
        self,
        msg: str,
        silent: bool = False,
        prepend: str = "",
        append: str = "",
        end: str = "\n",
        *args,
        **kwargs,
    ):
        self._logger.critical(self.add_uuid(msg), *args, **kwargs)
        if not silent:
            self._print(prepend + str(msg) + append, 7, end=end)
