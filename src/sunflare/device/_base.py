from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._protocols import PDevice

if TYPE_CHECKING:
    from bluesky.protocols import Descriptor, Reading

__all__ = ["Device"]


class Device(PDevice):
    """A boilerplate base class for quick device development.

    Users may subclass from this device and implement their own
    configuration properties and methods.

    Example usage:

    ```python
    from sunflare.device import Device
    from attrs import define


    class MyDevice(Device):
        def __init__(self, name: str, some_param: str, another_param: bool) -> None:
            super().__init__(name)
            self.some_param = some_param
            self.another_param = another_param

        def describe_configuration(self) -> dict[str, Descriptor]:
            return {
                "some_param": {
                    "source": self.name,
                    "dtype": "string",
                    "shape": [],
                },
                "another_param": {
                    "source": self.name,
                    "dtype": "boolean",
                    "shape": [],
                },
            }

        def read_configuration(self) -> dict[str, Reading[Any]]:
            import time

            return {
                "some_param": {"value": self.some_param, "timestamp": time.time()},
                "another_param": {
                    "value": self.another_param,
                    "timestamp": time.time(),
                },
            }
    ```

    Parameters
    ----------
    name : ``str``
        Name of the device. Serves as a unique identifier for the object created from it.
    """

    def __init__(self, name: str) -> None:
        self._name = name

    def describe_configuration(self) -> dict[str, Descriptor]:
        """Provide a description of the device configuration.

        Subclasses should override this method to provide their own
        configuration description compatible with the Bluesky event model.

        Returns
        -------
        dict[``str``, `event_model.DataKey`]
            A dictionary with the description of each field of the device configuration.
        """
        return {}

    def read_configuration(self) -> dict[str, Reading[Any]]:
        """Provide a description of the device configuration.

        Subclasses should override this method to provide their own
        configuration reading compatible with the Bluesky event model.

        Returns
        -------
        dict[``str``, `bluesky.protocols.Descriptor`]
            A dictionary with the description of each field of the device configuration.
        """
        return {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> None:
        return None
