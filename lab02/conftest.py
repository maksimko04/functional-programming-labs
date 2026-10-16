import pytest
from core import Parcel, Record


@pytest.fixture
def parcels() -> list[Parcel]:
    return [
        {
            "id": 1,
            "sender": "ivan petrenko",
            "region": "West",
            "delivery_parts": [50.0, 20.0],
        },
        {
            "id": 2,
            "sender": "OLHA SHEVCHENKO",
            "region": "East",
            "delivery_parts": [120.0],
        },
        {
            "id": 3,
            "sender": "petro ivanov",
            "region": "West",
            "delivery_parts": [10.0, 5.5],
        },
        {"id": 4, "sender": "maria koval", "region": "North", "delivery_parts": [84.0]},
        {
            "id": 5,
            "sender": "andrii bondar",
            "region": "East",
            "delivery_parts": [60.0, 24.0],
        },
    ]


@pytest.fixture
def records() -> list[Record]:
    return [
        {
            "id": 1,
            "name": "amit",
            "age": 30,
            "city": "Delhi",
            "purchases": [100.0, 50.0],
        },
        {"id": 2, "name": "neha", "age": 17, "city": "Delhi", "purchases": [500.0]},
        {"id": 3, "name": "raj", "age": 25, "city": "Mumbai", "purchases": [160.0]},
        {
            "id": 4,
            "name": "sita",
            "age": 40,
            "city": "Delhi",
            "purchases": [60.0, 40.0],
        },
    ]
