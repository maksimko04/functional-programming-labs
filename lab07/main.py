"""Демо-запуск ЛР7: завантаження тарифів із різних джерел і Top-N (I/O лише тут)."""

from __future__ import annotations

import sys
from pathlib import Path

from core import clean_and_rank, rank_tariffs, total_price
from loaders import load_tariffs, load_users

HERE = Path(__file__).parent


def main(argv: list[str]) -> None:
    """Друкує найкращі тарифи; аргументи: [min_minutes min_data min_sms]."""
    min_minutes = int(argv[0]) if argv else 300
    min_data = float(argv[1]) if len(argv) > 1 else 10.0
    min_sms = int(argv[2]) if len(argv) > 2 else 0

    rows_json = load_tariffs(HERE / "sample_data.json")
    rows_csv = load_tariffs(str(HERE / "sample_data.csv"))
    with open(HERE / "sample_data.json", encoding="utf-8") as f:
        rows_file = load_tariffs(f)
    print(f"json={len(rows_json)} csv={len(rows_csv)} file={len(rows_file)} rows")

    top = rank_tariffs(
        rows_json + rows_csv,
        top=3,
        min_minutes=min_minutes,
        min_data=min_data,
        min_sms=min_sms,
    )
    for t in top:
        print(
            f"{t.name:<14} {t.minutes:>5} min {t.data_gb:>5.1f} GB {t.sms:>4} sms "
            f"{t.price:>7.2f} score={t.score:.3f}"
        )
    print(f"total price of top: {total_price(top):.2f}")

    students = load_users(
        '[{"name": " alice ", "age": "19", "score": "8.5"}, '
        '{"name": "bob", "age": "17", "score": "9.1"}]'
    )
    print("students:", clean_and_rank(students, top=2))


if __name__ == "__main__":
    main(sys.argv[1:])
