"""Демо ЛР5: нескінченні потоки, вікна та ковзна статистика (варіант 13)."""

from __future__ import annotations

from collections.abc import Callable
from itertools import cycle, islice

from observations import first_n_stats, observations, window_max, window_range
from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    prefix_sums,
    take,
    window_sums,
)

SAMPLES = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]


def make_provider(values: list[float]) -> Callable[[], float]:
    """Детермінований постачальник: циклічно віддає значення зі списку."""
    source = cycle(values)
    return lambda: next(source)


def main() -> None:
    """Друкує приклади роботи потоків (єдиний I/O у лабораторній)."""
    print("fib first 10:", take(10, fib_stream()))
    print("fib drop 5 take 8:", take(8, drop(5, fib_stream())))
    print(
        "window sums of naturals (k=3, first 10):", take(10, window_sums(naturals(), 3))
    )
    print("moving average [1..6], k=2:", list(moving_average([1, 2, 3, 4, 5, 6], 2)))
    print("prefix sums [1,2,3,4]:", list(prefix_sums([1, 2, 3, 4])))

    stream = observations(make_provider(SAMPLES))
    print("window max (k=3, first 6):", list(islice(window_max(stream, 3), 6)))
    print("window range (k=3, first 6):", list(islice(window_range(SAMPLES, 3), 6)))
    for stats in first_n_stats(observations(make_provider(SAMPLES)), 3, 5):
        print(
            f"max={stats.maximum:.1f} min={stats.minimum:.1f} range={stats.spread:.1f}"
        )


if __name__ == "__main__":
    main()
