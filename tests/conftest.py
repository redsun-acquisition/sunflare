from pathlib import Path

import pytest

from sunflare.engine import RunEngine


@pytest.fixture
def config_path() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="module")
def RE() -> RunEngine:
    return RunEngine()
