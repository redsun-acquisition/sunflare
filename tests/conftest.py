from pathlib import Path

import pytest
import zmq

from typing import Generator
from sunflare.engine import RunEngine
from sunflare.virtual import VirtualBus


@pytest.fixture
def config_path() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="function")
def RE() -> RunEngine:
    return RunEngine()

@pytest.fixture(scope="function")
def bus() -> Generator[VirtualBus, None, None]:

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None

    _bus = VirtualBus()

    yield _bus

    _bus.shutdown()

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None
