from itertools import cycle, islice

import pytest
from hypothesis import given
from hypothesis import strategies as st
from observations import (
    WindowStats,
    first_n_stats,
    observations,
    window_max,
    window_min,
    window_range,
    window_stats,
)

SAMPLES = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]


def test_window_max_min_range() -> None:
    assert list(window_max(SAMPLES, 3)) == [4.0, 4.0, 5.0, 9.0, 9.0, 9.0]
    assert list(window_min(SAMPLES, 3)) == [1.0, 1.0, 1.0, 1.0, 2.0, 2.0]
    assert list(window_range(SAMPLES, 3)) == [3.0, 3.0, 4.0, 8.0, 7.0, 7.0]


def test_window_stats_matches_parts() -> None:
    stats = list(window_stats(SAMPLES, 4))
    assert stats[0] == WindowStats(4.0, 1.0, 3.0)
    assert [s.maximum for s in stats] == list(window_max(SAMPLES, 4))
    assert [s.minimum for s in stats] == list(window_min(SAMPLES, 4))


def test_first_n_from_infinite_stream() -> None:
    source = cycle(SAMPLES)
    stream = observations(lambda: next(source))
    assert first_n_stats(stream, 3, 2) == [
        WindowStats(4.0, 1.0, 3.0),
        WindowStats(4.0, 1.0, 3.0),
    ]
    assert list(islice(window_max(observations(lambda: 7.0), 2), 3)) == [7.0, 7.0, 7.0]


def test_edge_cases() -> None:
    assert list(window_max([], 2)) == []
    assert list(window_range([1.0, 2.0], 5)) == []
    assert first_n_stats(SAMPLES, 3, 0) == []
    with pytest.raises(ValueError):
        list(window_min(SAMPLES, 0))
    with pytest.raises(ValueError):
        first_n_stats(SAMPLES, 3, -1)


floats = st.lists(
    st.floats(allow_nan=False, allow_infinity=False, width=32), max_size=40
)


@given(floats, st.integers(min_value=1, max_value=6))
def test_property_range_is_non_negative_and_bounded(xs: list[float], k: int) -> None:
    for s in window_stats(xs, k):
        assert s.spread >= 0
        assert s.minimum <= s.maximum
        assert s.spread == s.maximum - s.minimum


@given(floats, st.integers(min_value=1, max_value=6))
def test_property_window_count(xs: list[float], k: int) -> None:
    expected = max(0, len(xs) - k + 1)
    assert len(list(window_max(xs, k))) == expected
    assert len(list(window_min(xs, k))) == expected


@given(floats, st.integers(min_value=1, max_value=6))
def test_property_matches_naive_slices(xs: list[float], k: int) -> None:
    naive = [max(xs[i : i + k]) for i in range(len(xs) - k + 1)]
    assert list(window_max(xs, k)) == naive
