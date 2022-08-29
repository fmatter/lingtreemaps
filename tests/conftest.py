from pathlib import Path
import pytest


@pytest.fixture
def data():
    return Path(__file__).parent / "data"
