"""Оболонка I/O та CLI для ЛР2: читання JSON, аргументи, друк (ядро — core.py)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core import (
    DeliveryStats,
    Parcel,
    build_delivery_pipeline,
    reduce_delivery_stats,
)

SAMPLE: list[Parcel] = [
    {
        "id": 1,
        "sender": "ivan petrenko",
        "region": "West",
        "delivery_parts": [50.0, 20.0],
    },
    {"id": 2, "sender": "OLHA SHEVCHENKO", "region": "East", "delivery_parts": [120.0]},
    {
        "id": 3,
        "sender": "petro ivanov",
        "region": "West",
        "delivery_parts": [10.0, 5.5],
    },
    {"id": 4, "sender": "maria koval", "region": "North", "delivery_parts": [84.0]},
    {
        "id": 5,
        "sender": "andrii bondar",
        "region": "East",
        "delivery_parts": [60.0, 24.0],
    },
]


def load_parcels(path: Path) -> list[Parcel]:
    """IO-адаптер: читає посилки з JSON-файлу."""
    return list(json.loads(path.read_text(encoding="utf-8")))


def render(top: list[Parcel], stats: DeliveryStats) -> str:
    """Перетворює чистий результат на текст (без друку)."""
    lines = [
        f"{p['id']:>3}  {p['sender']:<18} {p['region']:<6} {p['cost']:>8.2f}"
        for p in top
    ]
    return "\n".join(
        [
            *lines,
            f"count={stats['count']:.0f} delivery_sum={stats['delivery_sum']:.2f} "
            f"avg_delivery={stats['avg_delivery']:.2f}",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Розбір аргументів CLI."""
    parser = argparse.ArgumentParser(description="Top-N посилок за вартістю доставки")
    parser.add_argument("--data", type=Path, help="JSON зі списком посилок")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-region", default="West")
    parser.add_argument("--factor", type=float, default=1.2)
    parser.add_argument("--min-cost", type=float, default=0.0)
    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    """Точка входу: читання → чистий конвеєр → друк."""
    args = parse_args(argv)
    parcels = load_parcels(args.data) if args.data else SAMPLE
    pipeline = build_delivery_pipeline(
        args.top, args.boost_region, args.factor, args.min_cost
    )
    top = pipeline(parcels)
    print(render(top, reduce_delivery_stats(top)))


if __name__ == "__main__":
    main(sys.argv[1:])
