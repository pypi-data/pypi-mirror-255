"""
This module stores the placeholder arguments who's job it is to convert
arguments from the Dataset level `mpi`,  `omp`, `nodes`, etc. to what the
scheduler is expecting within a jobscript.

.. note::
    Placeholders without a `value` are "falsy". So checking their value in an
    if statment will return `True` if they have a value, `False` otherwise.
"""
from remotemanager.logging import LoggingMixin
from remotemanager.storage import SendableMixin


class placeholder_option(SendableMixin, LoggingMixin):
    """
    .. warning::
        This class is intended to be subclassed by the optional and required
        placeholders.

    Stub class to sit in place of an option within a computer.

    Args:
        mode (string):
            storage mode, required or optional
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc.)
    """

    def __init__(self, mode, flag, min, max):
        self._mode = mode
        self._flag = flag
        self._value = None
        self._bool = False

        self._min = min
        self._max = max

    def __hash__(self):
        return hash(self._mode)

    def __repr__(self):
        return str(self.value)

    def __bool__(self):
        """
        Makes objects "falsy" if no value has been set, "truthy" otherwise
        """
        return self.value is not None

    @property
    def flag(self):
        return self._flag

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def value(self):
        if hasattr(self, "default") and self._value is None:
            return self.default

        return self._value

    @value.setter
    def value(self, value):
        try:
            value / 1
            isnumeric = True
        except TypeError:
            isnumeric = False

        if isnumeric:
            if self.min is not None and value < self.min:
                raise ValueError(
                    f"{value} for {self.flag} is less than minimum value {self.min}"
                )
            if self.max is not None and value > self.max:
                raise ValueError(
                    f"{value} for {self.flag} is more than maximum value {self.max}"
                )

        self._bool = True
        self._value = value


class required(placeholder_option):
    """
    This option is _required_, and should raise an error if no value is found

    Args:
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc.)
    """

    def __init__(self, flag, min=None, max=None):
        super().__init__("required", flag, min, max)


class optional(placeholder_option):
    """
    This option is not required, and should have an accessible default if
    no value is found

    Args:
        flag (string):
            flag to append value to (`--nodes`, `--walltime`, etc.)
        default:
            default value to use if none is assigned
    """

    def __init__(self, flag, default=None, min=None, max=None):
        super().__init__("optional", flag, min, max)

        self._default = default

    @property
    def default(self):
        try:
            return self._default()
        except TypeError as E:
            self._logger.warning(f"recieved error from default attempt: {E}")
            return self._default


class runargs(dict):
    """
    Class to contain the dataset run_args in a way that won't break any loops
    over the resources

    Args:
        args (dict):
            Dataset run_args
    """

    _accesserror = (
        "\nParser is attempting to access the flag of the run_args, you "
        "should add an `if {option}: ...` catch to your parser."
        "\nRemember that placeholders without an argument are 'falsy', "
        "see the docs for more info. https://l_sim.gitlab.io/remotemanager"
        "/remotemanager.connection.computers.options.html"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __bool__(self):
        return False

    @property
    def value(self):
        """
        Prevents an AttributeError when a parser attempts to access the value.

        Returns:
            (dict): internal dict
        """
        return self.__dict__

    @property
    def flag(self):
        """
        Parsers should not access the flag method of the run_args, doing so likely
        means that a loop has iterated over this object and is attempting to insert
        it into a jobscript.

        Converts an AttributeError to one more tailored to the situation.

        Returns:
            RuntimeError
        """
        raise RuntimeError(runargs._accesserror)
