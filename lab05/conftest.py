import pytest


@pytest.fixture
def samples() -> list[float]:
    return [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
