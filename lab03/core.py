"""Чисті бізнес-функції над незмінною моделлю полісів (варіант 13).

Жодна функція не змінює вхідні об'єкти: кожне оновлення повертає новий Policy,
розрахунок премії кешується через lru_cache (можливо лише тому, що Policy хешований).
"""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from typing import Any

from model import Coverage, Policy, Risk

RISK_FACTORS: Mapping[Risk, float] = MappingProxyType(
    {"low": 0.9, "medium": 1.0, "high": 1.5}
)


def risk_factor(risks: frozenset[Risk]) -> float:
    """Добуток коефіцієнтів усіх ризиків полісу (порожня множина → 1.0)."""
    factor = 1.0
    for r in risks:
        factor *= RISK_FACTORS[r]
    return factor


@lru_cache(maxsize=1024)
def final_premium(policy: Policy) -> float:
    """Кінцева премія = базова премія × добуток коефіцієнтів ризику. Кешується."""
    return policy.base_premium() * risk_factor(policy.risks)


def add_coverage(policy: Policy, name: str, amount: float, rate: float) -> Policy:
    """Pure update: новий поліс із доданим покриттям."""
    return policy.add_coverage(Coverage(name, amount, rate))


def add_risk(policy: Policy, risk: Risk) -> Policy:
    """Pure update: новий поліс із доданим ризиком."""
    return policy.add_risk(risk)


def with_meta(policy: Policy, **updates: str) -> Policy:
    """Pure update: новий поліс із новою read-only meta (копія + оновлення)."""
    merged = {**policy.meta, **updates}
    return Policy(
        policy.id,
        policy.holder,
        policy.coverages,
        policy.risks,
        MappingProxyType(merged),
        policy.active,
    )


def recalculate(policy: Policy) -> tuple[Policy, float]:
    """Повертає той самий поліс і його кінцеву премію (кешовану)."""
    return policy, final_premium(policy)


def index_by_policy(policies: tuple[Policy, ...]) -> Mapping[Policy, float]:
    """Поліс як ключ словника (хешованість frozen dataclass) → премія."""
    return MappingProxyType({p: final_premium(p) for p in policies})


def freeze(obj: Any) -> Any:
    """Глибоке заморожування: dict → MappingProxyType, set → frozenset, list → tuple."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)
    return obj
