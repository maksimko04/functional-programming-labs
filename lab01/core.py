"""Чисте ядро: обробка замовлень інтернет-магазину (варіант 1).

Жодного I/O, глобального стану чи мутації вхідних даних.
Усі політики (фільтр, знижка, податок) передаються як Callable.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypedDict, TypeVar


class Item(TypedDict):
    price: float
    qty: int


class Order(TypedDict, total=False):
    id: int
    items: list[Item]
    paid: bool
    total: float


class Report(TypedDict):
    count: int
    revenue: float
    orders: list[Order]


FilterFn = Callable[[float], bool]
DiscountFn = Callable[[float], float]
TaxFn = Callable[[float], float]
Processor = Callable[[Iterable[Order]], Report]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def order_subtotal(order: Order) -> float:
    return sum(it["price"] * it["qty"] for it in order["items"])


def with_total(order: Order, total: float) -> Order:
    return {**order, "total": total}


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: DiscountFn,
    apply_tax: TaxFn,
) -> Processor:
    def process(orders: Iterable[Order]) -> Report:
        qualified = [
            with_total(o, apply_tax(apply_discount(order_subtotal(o))))
            for o in orders
            if o["paid"] and accept(order_subtotal(o))
        ]
        return {
            "count": len(qualified),
            "revenue": sum(o["total"] for o in qualified),
            "orders": qualified,
        }

    return process


def min_total_filter(min_total: float) -> FilterFn:
    return lambda subtotal: subtotal >= min_total


def percent_discount(rate: float) -> DiscountFn:
    return lambda amount: amount * (1 - rate)


def flat_tax(rate: float) -> TaxFn:
    return lambda amount: amount * (1 + rate)


def process_orders_pure(
    orders: Iterable[Order],
    *,
    min_total: float,
    discount: float,
    tax_rate: float,
) -> Report:
    process = make_processor(
        accept=min_total_filter(min_total),
        apply_discount=percent_discount(discount),
        apply_tax=flat_tax(tax_rate),
    )
    return process(orders)


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    return total, now()
