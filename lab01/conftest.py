import pytest

from core import Order


@pytest.fixture
def sample_orders() -> list[Order]:
    return [
        {"id": 1, "items": [{"price": 50.0, "qty": 3}], "paid": True},
        {"id": 2, "items": [{"price": 20.0, "qty": 1}], "paid": True},
        {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
        {"id": 4, "items": [{"price": 10.0, "qty": 10}, {"price": 5.5, "qty": 2}], "paid": True},
        {"id": 5, "items": [], "paid": True},
    ]
