"""Чисте ядро ЛР2: конвеєр перетворень над записами (варіант 13 — доставка посилок).

map/filter/reduce через генераторні вирази, композиція compose/pipe/juxt,
окрема reduce-агрегація. Жодних мутацій вхідних даних і жодного I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")


# --- композиція ---


def compose(*funcs: Callable[[A], A]) -> Callable[[A], A]:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""

    def _composed(x: A) -> A:
        for f in reversed(funcs):
            x = f(x)
        return x

    return _composed


def pipe(x: A, *funcs: Callable[[A], A]) -> A:
    """Конвеєр зліва направо: pipe(x, f, g) == g(f(x))."""
    return reduce(lambda acc, f: f(acc), funcs, x)


def juxt(*funcs: Callable[[A], B]) -> Callable[[A], tuple[B, ...]]:
    """juxt(f, g)(x) == (f(x), g(x)) — кілька поглядів на одне значення."""
    return lambda x: tuple(f(x) for f in funcs)


# --- варіант 13: доставка посилок ---


class Parcel(TypedDict, total=False):
    id: int
    sender: str
    region: str
    delivery_parts: list[float]
    cost: float


ParcelStep = Callable[[Iterable[Parcel]], Iterable[Parcel]]


class DeliveryStats(TypedDict):
    count: float
    delivery_sum: float
    avg_delivery: float


def with_cost() -> ParcelStep:
    """map: cost = сума частин вартості доставки (новий запис)."""
    return lambda parcels: (
        {**p, "cost": float(sum(p.get("delivery_parts", []) or []))} for p in parcels
    )


def boost_region(region: str, factor: float) -> ParcelStep:
    """map: регіональний коефіцієнт до вартості лише для заданого регіону."""

    def _boost(parcels: Iterable[Parcel]) -> Iterator[Parcel]:
        for p in parcels:
            cost = float(p.get("cost", 0.0))
            yield {**p, "cost": cost * factor if p.get("region") == region else cost}

    return _boost


def min_cost(threshold: float) -> ParcelStep:
    """filter: лишити посилки з вартістю не нижче порога."""
    return lambda parcels: filter(
        lambda p: float(p.get("cost", 0.0)) >= threshold, parcels
    )


def normalize_senders() -> ParcelStep:
    """map: ім'я відправника у Title Case без зайвих пробілів."""
    return lambda parcels: map(
        lambda p: {**p, "sender": str(p.get("sender", "")).strip().title()}, parcels
    )


def sort_by_cost_desc() -> ParcelStep:
    """sorted з двома ключами: вартість спадно, id зростом."""
    return lambda parcels: sorted(
        parcels, key=lambda p: (-float(p.get("cost", 0.0)), int(p.get("id", 0)))
    )


def take(n: int) -> ParcelStep:
    """Top-N через itertools.islice."""
    return lambda parcels: list(islice(parcels, n))


def reduce_delivery_stats(parcels: Iterable[Parcel]) -> DeliveryStats:
    """reduce-агрегація: count, delivery_sum, avg_delivery."""
    count, total = reduce(
        lambda acc, p: (acc[0] + 1, acc[1] + float(p.get("cost", 0.0))),
        parcels,
        (0.0, 0.0),
    )
    return {
        "count": count,
        "delivery_sum": total,
        "avg_delivery": total / count if count else 0.0,
    }


def build_delivery_pipeline(
    top_n: int = 3,
    region: str = "West",
    factor: float = 1.2,
    threshold: float = 0.0,
) -> Callable[[Iterable[Parcel]], list[Parcel]]:
    """Складає конвеєр варіанта 13 через compose; повертає чисту функцію."""
    steps = compose(
        take(top_n),
        sort_by_cost_desc(),
        min_cost(threshold),
        boost_region(region, factor),
        with_cost(),
        normalize_senders(),
    )
    return lambda parcels: list(steps(parcels))


# --- базовий приклад із методички: клієнти інтернет-магазину ---


class Record(TypedDict, total=False):
    id: int
    name: str
    age: int
    city: str
    purchases: list[float]
    total: float


RecordStep = Callable[[Iterable[Record]], Iterable[Record]]


class Stats(TypedDict):
    count: float
    sum_total: float
    avg_total: float


def only_adults(min_age: int = 18) -> RecordStep:
    """filter: повнолітні."""
    return lambda recs: (r for r in recs if int(r.get("age", 0)) >= min_age)


def with_total() -> RecordStep:
    """map: total = sum(purchases)."""
    return lambda recs: (
        {**r, "total": float(sum(r.get("purchases", []) or []))} for r in recs
    )


def boost_city(city: str, factor: float) -> RecordStep:
    """map: підсилити total для заданого міста."""

    def _boost(recs: Iterable[Record]) -> Iterator[Record]:
        for r in recs:
            t = float(r.get("total", 0.0))
            yield {**r, "total": t * factor if r.get("city") == city else t}

    return _boost


def normalize_names() -> RecordStep:
    """map: ім'я у Title Case."""
    return lambda recs: (
        {**r, "name": str(r.get("name", "")).strip().title()} for r in recs
    )


def sort_by_total_desc() -> RecordStep:
    """sorted: total спадно, id зростом."""
    return lambda recs: sorted(
        recs, key=lambda r: (-float(r.get("total", 0.0)), r.get("id", 0))
    )


def take_records(n: int) -> RecordStep:
    """Top-N для записів клієнтів."""
    return lambda recs: list(islice(recs, n))


def reduce_stats(recs: Iterable[Record]) -> Stats:
    """reduce-агрегація: count, sum_total, avg_total."""
    count, total = reduce(
        lambda acc, r: (acc[0] + 1, acc[1] + float(r.get("total", 0.0))),
        recs,
        (0.0, 0.0),
    )
    return {
        "count": count,
        "sum_total": total,
        "avg_total": total / count if count else 0.0,
    }


def build_pipeline(
    top_n: int = 2, city: str = "Delhi", factor: float = 1.1
) -> Callable[[Iterable[Record]], list[Record]]:
    """Конвеєр базового прикладу з методички."""
    steps = compose(
        take_records(top_n),
        sort_by_total_desc(),
        boost_city(city, factor),
        with_total(),
        only_adults(18),
        normalize_names(),
    )
    return lambda recs: list(steps(recs))
