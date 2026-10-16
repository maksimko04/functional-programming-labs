"""Доменні моделі ЛР7: Tariff із повним порядком через functools.total_ordering."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, eq=False)
class Tariff:
    """Мобільний тариф; порядок: score ↑, дешевший кращий, потім name."""

    name: str
    minutes: int
    data_gb: float
    sms: int
    price: float
    score: float = 0.0

    def _key(self) -> tuple[float, float, str]:
        return (self.score, -self.price, self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tariff):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Tariff):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())
