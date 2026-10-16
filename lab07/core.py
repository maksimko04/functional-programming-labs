"""Чисте ядро ЛР7: конвеєр на functools.partial / reduce та operator (варіант 13).

Предметна область — мобільні тарифні плани: name, minutes, data_gb, sms, price.
Жодних мутацій вхідних записів, жодного I/O.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller
from typing import Any, TypeVar

from models import Tariff

T = TypeVar("T")

Row = Mapping[str, Any]


def pipeline(value: T, *funcs: Callable[[Any], Any]) -> Any:
    """Протягує value через funcs зліва направо: pipeline(x, f, g) == g(f(x))."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[Any], Any]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """partial-обгортка над map: mapf(fn)(iterable)."""
    return partial(map, fn)


def filt(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """partial-обгортка над filter: filt(pred)(iterable)."""
    return partial(filter, pred)


# --- варіант 13: тарифи ---

get_name = itemgetter("name")
strip, title = methodcaller("strip"), methodcaller("title")


def normalize_tariff(row: Row) -> dict[str, Any]:
    """Новий запис із очищеною назвою та числовими полями."""
    return {
        "name": title(strip(str(get_name(row)))),
        "minutes": int(row["minutes"]),
        "data_gb": float(row["data_gb"]),
        "sms": int(row["sms"]),
        "price": float(row["price"]),
    }


def meets_requirements(
    row: Row, *, min_minutes: int = 0, min_data: float = 0.0, min_sms: int = 0
) -> bool:
    """Предикат: тариф задовольняє вимоги користувача (кожну окремо)."""
    return bool(
        row["minutes"] >= min_minutes
        and row["data_gb"] >= min_data
        and row["sms"] >= min_sms
    )


def score(
    row: Row, *, w_minutes: float = 0.1, w_data: float = 10.0, w_sms: float = 0.05
) -> float:
    """Цінність тарифу: зважена корисність на одиницю ціни."""
    value = row["minutes"] * w_minutes + row["data_gb"] * w_data + row["sms"] * w_sms
    return value / row["price"] if row["price"] > 0 else 0.0


def with_score(row: Row, scorer: Callable[[Row], float]) -> dict[str, Any]:
    """Новий запис із полем score, обчисленим scorer."""
    return {**row, "score": scorer(row)}


def to_tariff(row: Row) -> Tariff:
    """Перетворює словник на незмінний Tariff."""
    return Tariff(
        name=row["name"],
        minutes=row["minutes"],
        data_gb=row["data_gb"],
        sms=row["sms"],
        price=row["price"],
        score=row["score"],
    )


def rank_tariffs(
    rows: Iterable[Row],
    *,
    top: int = 3,
    min_minutes: int = 0,
    min_data: float = 0.0,
    min_sms: int = 0,
    w_minutes: float = 0.1,
    w_data: float = 10.0,
    w_sms: float = 0.05,
) -> list[Tariff]:
    """Конвеєр: нормалізація → фільтр за вимогами → score → сортування → Top-N."""
    accept = partial(
        meets_requirements, min_minutes=min_minutes, min_data=min_data, min_sms=min_sms
    )
    scorer = partial(score, w_minutes=w_minutes, w_data=w_data, w_sms=w_sms)
    result: list[Tariff] = pipeline(
        rows,
        mapf(normalize_tariff),
        filt(accept),
        mapf(partial(with_score, scorer=scorer)),
        mapf(to_tariff),
        partial(sorted, key=attrgetter("price", "name")),
        partial(sorted, key=attrgetter("score"), reverse=True),
        lambda it: list(it)[:top],
    )
    return result


def total_price(tariffs: Iterable[Tariff]) -> float:
    """reduce-агрегація: сумарна ціна вибраних тарифів."""
    return reduce(lambda acc, t: acc + t.price, tariffs, 0.0)


# --- базовий приклад з методички: студенти ---


def normalize_student(row: Row) -> dict[str, Any]:
    """Новий запис студента: name у Title Case, age → int, score → float."""
    return {
        "name": title(strip(str(get_name(row)))),
        "age": int(row["age"]),
        "score": float(row["score"]),
    }


def clean_and_rank(rows: Iterable[Row], top: int = 3) -> list[dict[str, Any]]:
    """Нормалізувати → повнолітні → score ↓, name ↑ → Top-N."""
    result: list[dict[str, Any]] = pipeline(
        rows,
        mapf(normalize_student),
        filt(lambda r: r["age"] >= 18),
        partial(sorted, key=itemgetter("name")),
        partial(sorted, key=itemgetter("score"), reverse=True),
        lambda it: list(it)[:top],
    )
    return result
