from pathlib import Path
from typing import Generator

import pytest
import zmq

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
    yield VirtualBus()
