from remotemanager.logging import Quiet


class LazyAppend:
    """
    Object which enables a lazy_append context manager

    """

    def __init__(self, parent):
        self._parent = parent

    def __enter__(self, *args, **kwargs):
        """
        When targeting a variable (``with ds.lazy_append() as var:``),

        `var` is what is returned from `__enter__`

        Thus, we need a copy of the class
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._parent.dependency is not None:
            for ds in self._parent.dependency.ds_list:
                ds.finish_append()
            # Since Quiet is global, setting it to False within the finish_append will
            # cause it to be also False in the subsequent calls
            Quiet.state = False
        else:
            self._parent.finish_append()

    def append_run(self, *args, **kwargs):
        kwargs["lazy"] = True
        self._parent.append_run(*args, **kwargs)
