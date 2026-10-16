from typing import Any

import pytest


@pytest.fixture
def rows() -> list[dict[str, Any]]:
    return [
        {
            "name": "  smart start ",
            "minutes": 300,
            "data_gb": 8,
            "sms": 50,
            "price": 150,
        },
        {
            "name": "FAMILY PLUS",
            "minutes": 1000,
            "data_gb": 25,
            "sms": 200,
            "price": 320,
        },
        {"name": "data max", "minutes": 200, "data_gb": 50, "sms": 0, "price": 300},
        {
            "name": "talk unlimited",
            "minutes": 3000,
            "data_gb": 5,
            "sms": 100,
            "price": 280,
        },
        {"name": "mini", "minutes": "100", "data_gb": "2", "sms": "20", "price": "80"},
    ]
