"""Незмінна модель страхових полісів (варіант 13).

Coverage і Policy — frozen dataclass зі slots; покриття у tuple, ризики у frozenset,
метадані клієнта — MappingProxyType поверх копії словника.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Literal

Risk = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class Coverage:
    """Одне покриття полісу: назва, страхова сума і ставка премії."""

    name: str
    amount: float
    rate: float

    def premium(self) -> float:
        """Премія за це покриття."""
        return self.amount * self.rate


@dataclass(frozen=True, slots=True)
class Policy:
    """Страховий поліс: покриття (tuple), ризики (frozenset), meta (read-only)."""

    id: int
    holder: str
    coverages: tuple[Coverage, ...]
    risks: frozenset[Risk]
    # mappingproxy не хешується → виключаємо з hash (у eq лишається)
    meta: Mapping[str, str] = field(hash=False)
    active: bool = True

    def base_premium(self) -> float:
        """Сума премій усіх покриттів без урахування ризиків."""
        return sum(c.premium() for c in self.coverages)

    def add_coverage(self, coverage: Coverage) -> Policy:
        """Новий поліс із доданим покриттям."""
        return replace(self, coverages=self.coverages + (coverage,))

    def add_risk(self, risk: Risk) -> Policy:
        """Новий поліс із доданим ризиком."""
        return replace(self, risks=self.risks | frozenset({risk}))

    def deactivate(self) -> Policy:
        """Новий поліс зі знятою активністю."""
        return replace(self, active=False)


def make_meta(**kwargs: str) -> Mapping[str, str]:
    """Read-only view над КОПІЄЮ словника, щоб ніхто не тримав посилання на оригінал."""
    return MappingProxyType(dict(kwargs))


def make_policy(
    id: int,
    holder: str,
    coverages: tuple[Coverage, ...] = (),
    risks: frozenset[Risk] = frozenset(),
    **meta: str,
) -> Policy:
    """Зручний конструктор полісу з read-only meta."""
    return Policy(id, holder, coverages, risks, make_meta(**meta))
