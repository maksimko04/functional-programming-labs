"""Чисте ядро: розрахунок страхових премій (варіант 13).

Жодного I/O, глобального стану чи мутації вхідних даних.
Усі політики (фільтр, коефіцієнт ризику, знижка за стаж) передаються як Callable.
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
Processor = Callable[[Iterable[Policy]], Report]
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def final_premium(base: float, risk_coef: float, discount: float) -> float:
    return base * risk_coef * (1 - discount)


def with_premium(policy: Policy, premium: float) -> Policy:
    return {**policy, "premium": premium}


def make_processor(
    *,
    accept: FilterFn,
    risk_factor: RiskFn,
    loyalty_discount: DiscountFn,
) -> Processor:
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
    process = make_processor(
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
