"""Property-based тести (Hypothesis) для конвеєра варіанта 13."""

from copy import deepcopy

from core import Parcel, build_delivery_pipeline, reduce_delivery_stats, with_cost
from hypothesis import given
from hypothesis import strategies as st

parcels_st = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1, max_value=10_000),
            "sender": st.text(min_size=1, max_size=12),
            "region": st.sampled_from(["West", "East", "North"]),
            "delivery_parts": st.lists(
                st.floats(min_value=0, max_value=1e4, allow_nan=False), max_size=5
            ),
        }
    ),
    max_size=30,
)


@given(parcels_st, st.integers(min_value=0, max_value=10))
def test_top_n_is_prefix_of_sorted(items: list[Parcel], n: int) -> None:
    full = build_delivery_pipeline(top_n=len(items) + 1)(items)
    top = build_delivery_pipeline(top_n=n)(items)
    assert top == full[:n]
    keys = [(-p["cost"], p["id"]) for p in full]
    assert keys == sorted(keys)


@given(parcels_st)
def test_pipeline_does_not_mutate(items: list[Parcel]) -> None:
    original = deepcopy(items)
    build_delivery_pipeline(top_n=5, threshold=10.0)(items)
    assert items == original


@given(parcels_st)
def test_stats_are_consistent(items: list[Parcel]) -> None:
    costed = list(with_cost()(items))
    stats = reduce_delivery_stats(costed)
    assert stats["count"] == len(items)
    assert abs(stats["delivery_sum"] - sum(p["cost"] for p in costed)) < 1e-6
    if items:
        assert (
            abs(stats["avg_delivery"] * stats["count"] - stats["delivery_sum"]) < 1e-6
        )
