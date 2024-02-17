from remotemanager.storage.sendablemixin import SendableMixin


class RunnerState(SendableMixin):
    """
    State tracker for a runner
    """

    _states = {
        "created": 0,  # runner exists
        "staged": 1,  # run files dumped to local dir
        "reset": 1,  # runner has been reset
        "dry run": 1,  # was staged and dry run
        "ready": 2,  # local files dumped, dataset files created. Ready to go
        "submit pending": 3,  # files were sent and command was executed
        "submitted": 4,  # confirmed running/queued by presence of an empty error file
        "completed": 5,  # valid result file exists
        "failed": 5,  # valid error file exists
        "satisfied": 6,  # files have been retrieved
    }

    def __init__(self, state: str = None):
        self._state = None
        self._success = None

        self.state = state

        if self.state == "completed":
            self._success = True
        elif self.state == "failed":
            self._success = False

        self.extra = None

    def __str__(self):
        if self.state is None:
            return "None"
        output = [self.state]
        if self.value > 5:
            output.append(f"(failed)" if self.failed else f"(success)")

        if self.extra is not None:
            output.append(f"({self.extra})")

        return " ".join(output)

    def __repr__(self):
        return f"RunnerState({self.state})"

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state not in RunnerState._states:
            raise ValueError(f"invalid state; {state}")

        self._state = state

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, success):
        self._success = success

    @property
    def failed(self):
        if self < "completed":
            return False
        return not self.success

    @property
    def value(self):
        return RunnerState._states[self.state]

    def _prepare_compare(self, other):
        if not isinstance(other, RunnerState):
            other = RunnerState(other)

        return other

    def __eq__(self, other):
        return self.state == self._prepare_compare(other).state

    def __lt__(self, other):
        return self.value < self._prepare_compare(other).value

    def __gt__(self, other):
        return self.value > self._prepare_compare(other).value

    def __le__(self, other):
        if self.value < self._prepare_compare(other).value:
            return True
        else:
            return self == other

    def __ge__(self, other):
        if self.value > self._prepare_compare(other).value:
            return True
        else:
            return self == other
