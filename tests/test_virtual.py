import logging
import threading
import time
import queue
from itertools import count

import pytest

from sunflare.virtual import Signal, VirtualBus


def test_virtual_bus_no_object(bus: VirtualBus) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    with pytest.raises(KeyError):
        bus.signals["MockOwner"]


def test_virtual_bus_psygnal_connection(bus: VirtualBus) -> None:
    """Tests the connection of signals in the virtual bus."""

    class FirstMockOwner:
        sigFirstSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus.signals["SecondMockOwner"]["sigSecondSignal"].connect(
                self.second_to_first
            )

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner:
        sigSecondSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus.signals["FirstMockOwner"]["sigFirstSignal"].connect(
                self.first_to_second
            )

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(bus)
    second_owner = SecondMockOwner(bus)

    first_owner.registration_phase()
    second_owner.registration_phase()

    first_owner.connection_phase()
    second_owner.connection_phase()

    assert "FirstMockOwner" in bus.signals
    assert "SecondMockOwner" in bus.signals

    first_owner.sigFirstSignal.emit(5)
    second_owner.sigSecondSignal.emit(5)


def test_virtual_bus_psygnal_connection_only(bus: VirtualBus) -> None:
    """Test "register_signals" using the 'only' parameter."""

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

    owner = MockOwner()

    bus.register_signals(owner, only=["sigSignalOne"])

    assert "MockOwner" in bus.signals
    assert len(bus.signals["MockOwner"]) == 1
    assert "sigSignalOne" in bus.signals["MockOwner"]
    assert "sigSignalTwo" not in bus.signals["MockOwner"]

    bus.signals["MockOwner"]["sigSignalOne"].connect(callback)
    owner.sigSignalOne.emit(5)
