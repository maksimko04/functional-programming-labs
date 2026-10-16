from copy import deepcopy

import pytest
from core import (
    Parcel,
    Record,
    boost_region,
    build_delivery_pipeline,
    build_pipeline,
    compose,
    juxt,
    min_cost,
    normalize_senders,
    pipe,
    reduce_delivery_stats,
    reduce_stats,
    sort_by_cost_desc,
    take,
    with_cost,
)

# --- варіант 13 ---


def test_top_n_order_and_tiebreak(parcels: list[Parcel]) -> None:
    top = build_delivery_pipeline(top_n=3, region="West", factor=1.2)(parcels)
    assert [p["id"] for p in top] == [2, 1, 4]
    assert top[1]["cost"] == pytest.approx(84.0)
    assert top[2]["cost"] == pytest.approx(84.0)


def test_tiebreak_by_id_when_costs_equal(parcels: list[Parcel]) -> None:
    top = build_delivery_pipeline(top_n=5, region="West", factor=1.2)(parcels)
    costs = [(p["cost"], p["id"]) for p in top]
    assert costs == sorted(costs, key=lambda c: (-c[0], c[1]))
    assert [p["id"] for p in top if p["cost"] == 84.0] == [1, 4, 5]


def test_no_mutation(parcels: list[Parcel]) -> None:
    original = deepcopy(parcels)
    build_delivery_pipeline(top_n=5, threshold=50.0)(parcels)
    reduce_delivery_stats(with_cost()(parcels))
    assert parcels == original


def test_threshold_filter(parcels: list[Parcel]) -> None:
    top = build_delivery_pipeline(top_n=10, region="None", factor=1.0, threshold=84.0)(
        parcels
    )
    assert [p["id"] for p in top] == [2, 4, 5]


def test_with_cost_and_boost(parcels: list[Parcel]) -> None:
    costed = list(with_cost()(parcels))
    assert [p["cost"] for p in costed] == [70.0, 120.0, 15.5, 84.0, 84.0]
    boosted = list(boost_region("West", 2.0)(costed))
    assert [p["cost"] for p in boosted] == [140.0, 120.0, 31.0, 84.0, 84.0]
    assert "cost" not in parcels[0]


def test_normalize_senders(parcels: list[Parcel]) -> None:
    names = [p["sender"] for p in normalize_senders()(parcels)]
    assert names[:2] == ["Ivan Petrenko", "Olha Shevchenko"]


def test_reduce_delivery_stats(parcels: list[Parcel]) -> None:
    stats = reduce_delivery_stats(with_cost()(parcels))
    assert stats["count"] == 5
    assert stats["delivery_sum"] == pytest.approx(373.5)
    assert stats["avg_delivery"] == pytest.approx(74.7)
    assert reduce_delivery_stats([]) == {
        "count": 0.0,
        "delivery_sum": 0.0,
        "avg_delivery": 0.0,
    }


def test_composition_equals_manual_steps(parcels: list[Parcel]) -> None:
    manual = take(2)(
        sort_by_cost_desc()(
            min_cost(80.0)(boost_region("East", 1.5)(with_cost()(parcels)))
        )
    )
    composed = compose(
        take(2),
        sort_by_cost_desc(),
        min_cost(80.0),
        boost_region("East", 1.5),
        with_cost(),
    )
    assert list(composed(parcels)) == list(manual)
    assert [p["id"] for p in manual] == [2, 5]


def test_pipe_and_juxt() -> None:
    assert pipe(3, lambda x: x + 1, lambda x: x * 2) == 8
    assert compose(lambda x: x * 2, lambda x: x + 1)(3) == 8

    def length(xs: list[int]) -> int:
        return len(xs)

    def total(xs: list[int]) -> int:
        return sum(xs)

    assert juxt(length, total)([3, 1, 2]) == (3, 6)


# --- базовий приклад з методички ---


def test_base_pipeline_top_n(records: list[Record]) -> None:
    top = build_pipeline(top_n=2, city="Delhi", factor=1.1)(records)
    assert [r["id"] for r in top] == [1, 3]
    assert top[0]["name"] == "Amit"
    assert top[0]["total"] == pytest.approx(165.0)


def test_base_reduce_stats(records: list[Record]) -> None:
    stats = reduce_stats(build_pipeline(top_n=10)(records))
    assert stats["count"] == 3
    assert stats["sum_total"] == pytest.approx(165.0 + 160.0 + 110.0)
    assert stats["avg_total"] == pytest.approx(435.0 / 3)


def test_base_no_mutation(records: list[Record]) -> None:
    original = deepcopy(records)
    build_pipeline()(records)
    assert records == original
