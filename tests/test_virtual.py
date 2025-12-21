import logging
import threading
import time
import queue
from itertools import count

import pytest

from sunflare.virtual import Signal, VirtualBus
from sunflare.log import Loggable


def test_virtual_bus_no_object(
    caplog: pytest.LogCaptureFixture, bus: VirtualBus
) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    signals = bus["MockOwner"]

    assert len(signals) == 0
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Class MockOwner not found in the registry."


def test_virtual_bus_psygnal_connection(bus: VirtualBus) -> None:
    """Tests the connection of signals in the virtual bus."""

    class FirstMockOwner:
        sigFirstSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus["SecondMockOwner"]["sigSecondSignal"].connect(self.second_to_first)

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner:
        sigSecondSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus["FirstMockOwner"]["sigFirstSignal"].connect(self.first_to_second)

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(bus)
    second_owner = SecondMockOwner(bus)

    first_owner.registration_phase()
    second_owner.registration_phase()

    first_owner.connection_phase()
    second_owner.connection_phase()

    assert "FirstMockOwner" in bus
    assert "SecondMockOwner" in bus

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

    assert "MockOwner" in bus
    assert len(bus["MockOwner"]) == 1
    assert "sigSignalOne" in bus["MockOwner"]
    assert "sigSignalTwo" not in bus["MockOwner"]

    bus["MockOwner"]["sigSignalOne"].connect(callback)
    owner.sigSignalOne.emit(5)
