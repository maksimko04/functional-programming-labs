from collections.abc import Iterator
from itertools import islice

from observations import observations, window_max
from streams import drop, moving_average, sliding_window, take


class CountingSource:
    """Ітератор, що рахує, скільки елементів у нього реально запитали."""

    def __init__(self) -> None:
        self.pulled = 0

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        self.pulled += 1
        return self.pulled


def test_take_pulls_exactly_n() -> None:
    src = CountingSource()
    assert take(4, src) == [1, 2, 3, 4]
    assert src.pulled == 4


def test_sliding_window_pulls_only_what_is_consumed() -> None:
    src = CountingSource()
    windows = sliding_window(src, 3)
    assert src.pulled == 0  # генератор ще не стартував
    assert next(windows) == (1, 2, 3)
    assert src.pulled == 3
    assert next(windows) == (2, 3, 4)
    assert src.pulled == 4


def test_pipeline_is_lazy_end_to_end() -> None:
    src = CountingSource()
    pipeline = moving_average(drop(2, src), 2)
    assert src.pulled == 2  # drop промотує n елементів одразу, вікна ще не стартували
    assert list(islice(pipeline, 2)) == [3.5, 4.5]
    assert src.pulled == 5  # 2 пропущено + 3 для двох вікон по 2


def test_provider_called_on_demand_only() -> None:
    calls = {"n": 0}

    def provider() -> float:
        calls["n"] += 1
        return float(calls["n"])

    stream = window_max(observations(provider), 2)
    assert calls["n"] == 0
    assert list(islice(stream, 3)) == [2.0, 3.0, 4.0]
    assert calls["n"] == 4
