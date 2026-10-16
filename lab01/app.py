"""Оболонка побічних ефектів: читання JSON, друк звіту, годинник."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from core import Policy, Report, process_policies_pure, stamp_total

RISK_RATES = {"low": 0.9, "medium": 1.0, "high": 1.5}

SAMPLE: list[Policy] = [
    {"id": 1, "base_premium": 1000.0, "risk": "low", "years": 5, "active": True},
    {"id": 2, "base_premium": 300.0, "risk": "high", "years": 0, "active": True},
    {"id": 3, "base_premium": 2000.0, "risk": "medium", "years": 20, "active": False},
    {"id": 4, "base_premium": 1500.0, "risk": "high", "years": 20, "active": True},
]


def load_policies(path: Path) -> list[Policy]:
    return list(json.loads(path.read_text(encoding="utf-8")))


def render_report(result: Report) -> str:
    lines = [
        f"Policy: {p['id']} premium: {p['premium']:.2f}" for p in result["policies"]
    ]
    return "\n".join(
        [*lines, f"Count: {result['count']}", f"Total: {result['total_premium']:.2f}"]
    )


def main(argv: list[str]) -> None:
    policies = load_policies(Path(argv[1])) if len(argv) > 1 else SAMPLE
    result = process_policies_pure(
        policies,
        min_premium=500,
        risk_rates=RISK_RATES,
        discount_per_year=0.02,
        max_discount=0.3,
    )
    print(render_report(result))
    total, stamp = stamp_total(result["total_premium"], time.time)
    print(f"Stamped: {total:.2f} at {time.strftime('%H:%M:%S', time.localtime(stamp))}")


if __name__ == "__main__":
    main(sys.argv)
