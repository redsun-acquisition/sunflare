import os

import pytest


@pytest.fixture
def config_path() -> str:
    return os.path.join(os.path.dirname(__file__), "data")
