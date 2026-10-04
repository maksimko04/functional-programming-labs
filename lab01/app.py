"""Оболонка побічних ефектів: читання JSON, друк звіту, годинник."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from core import Order, Report, process_orders_pure, stamp_total

SAMPLE: list[Order] = [
    {"id": 1, "items": [{"price": 50.0, "qty": 3}], "paid": True},
    {"id": 2, "items": [{"price": 20.0, "qty": 1}], "paid": True},
    {"id": 3, "items": [{"price": 200.0, "qty": 1}], "paid": False},
    {"id": 4, "items": [{"price": 10.0, "qty": 10}, {"price": 5.5, "qty": 2}], "paid": True},
]


def load_orders(path: Path) -> list[Order]:
    return list(json.loads(path.read_text(encoding="utf-8")))


def render_report(result: Report) -> str:
    lines = [f"Processed: {o['id']} total: {o['total']:.2f}" for o in result["orders"]]
    return "\n".join([*lines, f"Count: {result['count']}", f"Revenue: {result['revenue']:.2f}"])


def main(argv: list[str]) -> None:
    orders = load_orders(Path(argv[1])) if len(argv) > 1 else SAMPLE
    result = process_orders_pure(orders, min_total=100, discount=0.1, tax_rate=0.2)
    print(render_report(result))
    revenue, stamp = stamp_total(result["revenue"], time.time)
    print(f"Stamped: {revenue:.2f} at {time.strftime('%H:%M:%S', time.localtime(stamp))}")


if __name__ == "__main__":
    main(sys.argv)
