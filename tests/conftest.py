from pathlib import Path

import pytest
import zmq

from typing import Generator
from sunflare.engine import RunEngine
from sunflare.virtual import VirtualBus, Signal


@pytest.fixture
def config_path() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="function")
def RE() -> RunEngine:
    return RunEngine()

class MockVirtualBus(VirtualBus):
    sigMySignal = Signal(int, description="My signal")

@pytest.fixture(scope="function")
def bus() -> Generator[MockVirtualBus, None, None]:

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None

    _bus = MockVirtualBus()

    yield _bus

    _bus.shutdown()

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None
