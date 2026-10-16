"""Варіант 13 — ковзні максимуми: лінива статистика по вікнах потоку спостережень.

Потік спостережень може бути нескінченним (генератор з інжектованим постачальником
значень), тому всі функції повертають ітератори, а результат обмежується take/islice.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from itertools import islice
from typing import NamedTuple

from streams import sliding_window


class WindowStats(NamedTuple):
    """Статистика одного вікна: максимум, мінімум і розмах."""

    maximum: float
    minimum: float
    spread: float


def observations(provider: Callable[[], float]) -> Iterator[float]:
    """Нескінченний потік спостережень; значення береться з provider лише за запитом."""
    while True:
        yield provider()


def window_max(it: Iterable[float], k: int) -> Iterator[float]:
    """Ковзний максимум по вікнах розміру k."""
    return map(max, sliding_window(it, k))


def window_min(it: Iterable[float], k: int) -> Iterator[float]:
    """Ковзний мінімум по вікнах розміру k."""
    return map(min, sliding_window(it, k))


def window_range(it: Iterable[float], k: int) -> Iterator[float]:
    """Ковзний розмах (max - min) по вікнах розміру k."""
    return (max(w) - min(w) for w in sliding_window(it, k))


def window_stats(it: Iterable[float], k: int) -> Iterator[WindowStats]:
    """Ковзна статистика (max, min, range) по вікнах розміру k одним проходом."""
    return (WindowStats(max(w), min(w), max(w) - min(w)) for w in sliding_window(it, k))


def first_n_stats(it: Iterable[float], k: int, n: int) -> list[WindowStats]:
    """Перші n результатів ковзної статистики (єдина матеріалізація — на виході)."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return list(islice(window_stats(it, k), n))
