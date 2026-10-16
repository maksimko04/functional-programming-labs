import pytest
from core import Order, Policy


@pytest.fixture
def sample_policies() -> list[Policy]:
    return [
        {"id": 1, "base_premium": 1000.0, "risk": "low", "years": 5, "active": True},
        {"id": 2, "base_premium": 300.0, "risk": "high", "years": 0, "active": True},
        {
            "id": 3,
            "base_premium": 2000.0,
            "risk": "medium",
            "years": 20,
            "active": False,
        },
        {"id": 4, "base_premium": 1500.0, "risk": "high", "years": 20, "active": True},
        {"id": 5, "base_premium": 500.0, "risk": "medium", "years": 1, "active": True},
    ]


@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "items": [{"price": 50.0, "qty": 3}], "paid": True},
        {"id": 2, "items": [{"price": 20.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
        {
            "id": 4,
            "items": [{"price": 10.0, "qty": 10}, {"price": 5.5, "qty": 2}],
            "paid": True,
        },
    ]
