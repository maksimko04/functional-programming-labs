"""Property-based тести (Hypothesis) для конвеєра тарифів."""

from copy import deepcopy
from typing import Any

from core import rank_tariffs
from hypothesis import given
from hypothesis import strategies as st
from models import Tariff

rows_st = st.lists(
    st.fixed_dictionaries(
        {
            "name": st.text(min_size=1, max_size=10),
            "minutes": st.integers(min_value=0, max_value=5000),
            "data_gb": st.floats(min_value=0, max_value=100, allow_nan=False),
            "sms": st.integers(min_value=0, max_value=1000),
            "price": st.floats(min_value=1, max_value=1000, allow_nan=False),
        }
    ),
    max_size=25,
)


@given(rows_st, st.integers(min_value=0, max_value=10))
def test_top_is_prefix_of_sorted(rows: list[dict[str, Any]], n: int) -> None:
    full = rank_tariffs(rows, top=len(rows) + 1)
    assert rank_tariffs(rows, top=n) == full[:n]
    assert full == sorted(full, key=lambda t: (-t.score, t.price, t.name))


@given(rows_st)
def test_no_mutation(rows: list[dict[str, Any]]) -> None:
    original = deepcopy(rows)
    rank_tariffs(rows, top=5, min_minutes=100)
    assert rows == original


@given(rows_st, st.integers(min_value=0, max_value=5000))
def test_filter_respects_min_minutes(rows: list[dict[str, Any]], m: int) -> None:
    top = rank_tariffs(rows, top=100, min_minutes=m)
    assert all(isinstance(t, Tariff) and t.minutes >= m for t in top)
    assert len(top) == sum(1 for r in rows if r["minutes"] >= m)
