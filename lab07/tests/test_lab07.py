from copy import deepcopy
from functools import partial
from operator import attrgetter, itemgetter, methodcaller
from pathlib import Path
from typing import Any

import pytest
from core import (
    clean_and_rank,
    filt,
    mapf,
    meets_requirements,
    normalize_tariff,
    pipeline,
    rank_tariffs,
    score,
    total_price,
)
from loaders import load_tariffs, load_users
from models import Tariff

# --- pipeline / partial / operator ---


def test_pipeline_applies_left_to_right() -> None:
    assert pipeline(3, lambda x: x + 1, lambda x: x * 2, lambda x: x + 1) == 9
    assert pipeline(5) == 5


def test_mapf_filt_are_partials() -> None:
    assert isinstance(mapf(str), partial) and isinstance(filt(bool), partial)
    assert list(
        pipeline([1, 2, 3, 4], filt(lambda x: x % 2 == 0), mapf(lambda x: x * 10))
    ) == [
        20,
        40,
    ]


def test_partial_requirements_and_score() -> None:
    accept = partial(meets_requirements, min_minutes=500, min_data=10.0)
    assert accept({"minutes": 500, "data_gb": 10.0, "sms": 0}) is True
    assert accept({"minutes": 499, "data_gb": 50.0, "sms": 0}) is False
    cheap = partial(score, w_minutes=0.0, w_data=1.0, w_sms=0.0)
    assert cheap({"minutes": 0, "data_gb": 20.0, "sms": 0, "price": 10.0}) == 2.0
    assert score({"minutes": 1, "data_gb": 1.0, "sms": 1, "price": 0.0}) == 0.0


def test_operator_helpers() -> None:
    rows = [{"a": 1, "b": 2}, {"a": 1, "b": 1}, {"a": 0, "b": 9}]
    assert sorted(rows, key=itemgetter("a", "b")) == [
        {"a": 0, "b": 9},
        {"a": 1, "b": 1},
        {"a": 1, "b": 2},
    ]
    assert methodcaller("title")(methodcaller("strip")("  aLiCe ")) == "Alice"
    t = Tariff("x", 1, 1.0, 1, 10.0, 0.5)
    assert attrgetter("price", "name")(t) == (10.0, "x")


# --- варіант 13: конвеєр тарифів ---


def test_normalize_creates_new_record(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    out = normalize_tariff(rows[0])
    assert out == {
        "name": "Smart Start",
        "minutes": 300,
        "data_gb": 8.0,
        "sms": 50,
        "price": 150.0,
    }
    assert rows == original


def test_rank_tariffs_top_n_and_order(rows: list[dict[str, Any]]) -> None:
    top = rank_tariffs(rows, top=2, min_minutes=200, min_data=5.0)
    assert [t.name for t in top] == ["Data Max", "Talk Unlimited"]
    assert top[0].score >= top[1].score
    assert len(rank_tariffs(rows, top=10)) == 5


def test_rank_tariffs_filters_and_tiebreak() -> None:
    same = [
        {"name": "b", "minutes": 100, "data_gb": 1, "sms": 0, "price": 10},
        {"name": "a", "minutes": 100, "data_gb": 1, "sms": 0, "price": 10},
        {"name": "c", "minutes": 200, "data_gb": 2, "sms": 0, "price": 20},
    ]
    top = rank_tariffs(same, top=3)
    assert [t.name for t in top] == ["A", "B", "C"]
    assert rank_tariffs(same, top=3, min_sms=1) == []


def test_total_price_reduce(rows: list[dict[str, Any]]) -> None:
    top = rank_tariffs(rows, top=2)
    assert total_price(top) == pytest.approx(sum(t.price for t in top))
    assert total_price([]) == 0.0


def test_no_mutation(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    rank_tariffs(rows, top=5, min_minutes=100)
    assert rows == original


# --- singledispatch ---

JSON = '[{"name": "a", "minutes": 1, "data_gb": 1, "sms": 1, "price": 1}]'
CSV = "name,minutes,data_gb,sms,price\na,1,1,1,1\n"


def test_load_from_all_sources(tmp_path: Path) -> None:
    pj, pc = tmp_path / "t.json", tmp_path / "t.csv"
    pj.write_text(JSON, encoding="utf-8")
    pc.write_text(CSV, encoding="utf-8")
    expected = load_tariffs(JSON)
    assert expected[0]["name"] == "a"
    assert load_tariffs(str(pj)) == expected
    assert load_tariffs(pj) == expected
    assert load_tariffs(expected) == expected
    with open(pj, encoding="utf-8") as f:
        assert load_tariffs(f) == expected
    with open(pc, encoding="utf-8") as f:
        assert load_tariffs(f)[0]["name"] == "a"
    csv_rows = load_tariffs(pc)
    assert csv_rows[0] == {
        "name": "a",
        "minutes": "1",
        "data_gb": "1",
        "sms": "1",
        "price": "1",
    }
    assert rank_tariffs(csv_rows) == rank_tariffs(expected)


def test_load_rejects_bad_input() -> None:
    with pytest.raises(TypeError):
        load_tariffs(42)
    with pytest.raises(ValueError):
        load_tariffs([1, 2])
    with pytest.raises(ValueError):
        load_tariffs('{"name": "x"}')


# --- total_ordering ---


def test_tariff_ordering() -> None:
    a = Tariff("a", 1, 1.0, 1, 10.0, score=2.0)
    b = Tariff("b", 1, 1.0, 1, 20.0, score=2.0)
    c = Tariff("c", 1, 1.0, 1, 5.0, score=1.0)
    assert c < b < a
    assert a > b and a >= b and c <= b and a != b
    assert a == Tariff("a", 9, 9.0, 9, 10.0, score=2.0)
    assert sorted([a, c, b]) == [c, b, a] and max([a, b, c]) is a
    assert len({a, b, c, Tariff("a", 9, 9.0, 9, 10.0, score=2.0)}) == 3


def test_tariff_not_implemented_for_other_types() -> None:
    t = Tariff("a", 1, 1.0, 1, 10.0)
    assert t.__eq__("x") is NotImplemented
    assert t.__lt__("x") is NotImplemented
    assert t != "x"
    with pytest.raises(TypeError):
        _ = t < "x"


# --- базовий приклад з методички ---


def test_clean_and_rank_students() -> None:
    rows = load_users(
        '[{"name": "  ALICE  ", "age": "19", "score": "8.5"},'
        ' {"name": "bob", "age": "17", "score": "9.1"},'
        ' {"name": "Carol", "age": "21", "score": "7.0"},'
        ' {"name": "denis", "age": "20", "score": "9.3"}]'
    )
    assert clean_and_rank(rows, top=2) == [
        {"name": "Denis", "age": 20, "score": 9.3},
        {"name": "Alice", "age": 19, "score": 8.5},
    ]
