"""Чисте ядро: страхові премії (варіант 13) і базове завдання (замовлення).

Жодного I/O, глобального стану чи мутації вхідних даних.
Усі політики передаються як Callable.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TypedDict, TypeVar


class Policy(TypedDict, total=False):
    id: int
    base_premium: float
    risk: str
    years: int
    active: bool
    premium: float


class Report(TypedDict):
    count: int
    total_premium: float
    policies: list[Policy]


FilterFn = Callable[[float], bool]
RiskFn = Callable[[str], float]
DiscountFn = Callable[[int], float]
AmountFn = Callable[[float], float]
PolicyProcessor = Callable[[Iterable[Policy]], Report]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def final_premium(base: float, risk_coef: float, discount: float) -> float:
    return base * risk_coef * (1 - discount)


def with_premium(policy: Policy, premium: float) -> Policy:
    return {**policy, "premium": premium}


def make_policy_processor(
    *,
    accept: FilterFn,
    risk_factor: RiskFn,
    loyalty_discount: DiscountFn,
) -> PolicyProcessor:
    def process(policies: Iterable[Policy]) -> Report:
        qualified = [
            with_premium(
                p,
                final_premium(
                    p["base_premium"],
                    risk_factor(p["risk"]),
                    loyalty_discount(p["years"]),
                ),
            )
            for p in policies
            if p["active"] and accept(p["base_premium"])
        ]
        return {
            "count": len(qualified),
            "total_premium": sum(p["premium"] for p in qualified),
            "policies": qualified,
        }

    return process


def min_premium_filter(min_premium: float) -> FilterFn:
    return lambda base: base >= min_premium


def table_risk(rates: Mapping[str, float], default: float = 1.0) -> RiskFn:
    return lambda risk: rates.get(risk, default)


def years_discount(rate_per_year: float, max_discount: float) -> DiscountFn:
    return lambda years: min(years * rate_per_year, max_discount)


def process_policies_pure(
    policies: Iterable[Policy],
    *,
    min_premium: float,
    risk_rates: Mapping[str, float],
    discount_per_year: float,
    max_discount: float,
) -> Report:
    process = make_policy_processor(
        accept=min_premium_filter(min_premium),
        risk_factor=table_risk(risk_rates),
        loyalty_discount=years_discount(discount_per_year, max_discount),
    )
    return process(policies)


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    return total, now()


# --- базове завдання з методички: замовлення інтернет-магазину ---


class Item(TypedDict):
    price: float
    qty: int


class Order(TypedDict, total=False):
    id: int
    items: list[Item]
    paid: bool
    total: float


class OrderReport(TypedDict):
    count: int
    revenue: float
    orders: list[Order]


Processor = Callable[[Iterable[Order]], OrderReport]


def order_subtotal(order: Order) -> float:
    return sum(it["price"] * it["qty"] for it in order["items"])


def with_total(order: Order, total: float) -> Order:
    return {**order, "total": total}


def make_processor(
    *,
    accept: FilterFn,
    apply_discount: AmountFn,
    apply_tax: AmountFn,
) -> Processor:
    def process(orders: Iterable[Order]) -> OrderReport:
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


def process_orders_pure(
    orders: Iterable[Order],
    *,
    min_total: float,
    discount: float,
    tax_rate: float,
) -> OrderReport:
    process = make_processor(
        accept=lambda subtotal: subtotal >= min_total,
        apply_discount=lambda amount: amount * (1 - discount),
        apply_tax=lambda amount: amount * (1 + tax_rate),
    )
    return process(orders)
