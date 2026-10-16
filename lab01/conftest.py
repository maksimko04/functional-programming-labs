import pytest

from core import Policy


@pytest.fixture
def sample_policies() -> list[Policy]:
    return [
        {"id": 1, "base_premium": 1000.0, "risk": "low", "years": 5, "active": True},
        {"id": 2, "base_premium": 300.0, "risk": "high", "years": 0, "active": True},
        {"id": 3, "base_premium": 2000.0, "risk": "medium", "years": 20, "active": False},
        {"id": 4, "base_premium": 1500.0, "risk": "high", "years": 20, "active": True},
        {"id": 5, "base_premium": 500.0, "risk": "medium", "years": 1, "active": True},
    ]
