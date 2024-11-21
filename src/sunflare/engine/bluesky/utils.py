"""Module for extra utilities which are inherent to the Bluesky interface."""


class Status:
    """Status object compatible with Bluesky `Status` protocol."""

    def __init__(self) -> None:
        self._done = False
        self._success = False

    @property
    def done(self) -> bool:
        """If done return True, otherwise return False."""
        return self._done

    @done.setter
    def done(self, value: bool) -> None:
        self._done = value

    @property
    def success(self) -> bool:
        """If done return whether the operation was successful."""
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        self._success = value
