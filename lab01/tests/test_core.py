from copy import deepcopy

import pytest

from app import render_report
from core import (
    Order,
    compose,
    flat_tax,
    make_multiplier,
    make_processor,
    min_total_filter,
    order_subtotal,
    percent_discount,
    process_orders_pure,
    stamp_total,
    with_total,
)
from starter_imperative import process_orders

ARGS = {"min_total": 100.0, "discount": 0.1, "tax_rate": 0.2}


def test_referential_transparency(sample_orders: list[Order]) -> None:
    r1 = process_orders_pure(sample_orders, **ARGS)
    r2 = process_orders_pure(sample_orders, **ARGS)
    assert r1 == r2


def test_no_mutation(sample_orders: list[Order]) -> None:
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original


def test_matches_imperative(sample_orders: list[Order]) -> None:
    expected = process_orders(deepcopy(sample_orders), 100, 0.1)
    assert process_orders_pure(sample_orders, **ARGS) == expected


def test_filters_unpaid_and_small(sample_orders: list[Order]) -> None:
    result = process_orders_pure(sample_orders, **ARGS)
    assert [o["id"] for o in result["orders"]] == [1, 4]
    assert result["count"] == 2
    assert result["revenue"] == pytest.approx(150 * 0.9 * 1.2 + 111 * 0.9 * 1.2)


def test_order_subtotal() -> None:
    assert order_subtotal({"id": 1, "items": [{"price": 2.5, "qty": 4}], "paid": True}) == 10.0
    assert order_subtotal({"id": 2, "items": [], "paid": True}) == 0.0


def test_with_total_returns_new_dict() -> None:
    order: Order = {"id": 1, "items": [], "paid": True}
    new = with_total(order, 42.0)
    assert new == {"id": 1, "items": [], "paid": True, "total": 42.0}
    assert "total" not in order
    assert new is not order


def test_callable_policies(sample_orders: list[Order]) -> None:
    process = make_processor(
        accept=lambda s: s >= 50,
        apply_discount=lambda s: s * 0.9,
        apply_tax=lambda s: s * 1.2,
    )
    result = process(sample_orders)
    assert [o["id"] for o in result["orders"]] == [1, 4]
    assert result["revenue"] == pytest.approx((150 + 111) * 0.9 * 1.2)


def test_policy_factories() -> None:
    assert min_total_filter(100)(99.9) is False
    assert min_total_filter(100)(100) is True
    assert percent_discount(0.25)(200) == 150.0
    assert flat_tax(0.2)(100) == pytest.approx(120.0)


def test_compose_and_multiplier() -> None:
    discount = compose(flat_tax(0.2), percent_discount(0.5))
    assert discount(100) == pytest.approx(60.0)
    assert make_multiplier(3)(7) == 21
    assert compose(make_multiplier(2), make_multiplier(5))(1) == 10


def test_stamp_total_uses_injected_clock() -> None:
    assert stamp_total(10.0, lambda: 123.0) == (10.0, 123.0)


def test_render_report(sample_orders: list[Order]) -> None:
    text = render_report(process_orders_pure(sample_orders, **ARGS))
    assert text.splitlines() == [
        "Processed: 1 total: 162.00",
        "Processed: 4 total: 119.88",
        "Count: 2",
        "Revenue: 281.88",
    ]
