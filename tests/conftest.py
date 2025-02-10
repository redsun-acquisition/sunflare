from pathlib import Path

import pytest


@pytest.fixture
def config_path() -> Path:
    return Path(__file__).parent / "data"
