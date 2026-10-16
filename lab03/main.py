"""Демонстрація pure-оновлень незмінного полісу (лише друк, логіка в core/model)."""

from __future__ import annotations

from core import add_coverage, add_risk, final_premium, index_by_policy, with_meta
from model import Coverage, make_policy


def main() -> None:
    """Створює поліс, виконує три pure-оновлення і показує, що оригінал не змінився."""
    p0 = make_policy(
        1,
        "Ivan Petrenko",
        (Coverage("car", 10_000.0, 0.05),),
        frozenset({"low"}),
        source="web",
    )
    p1 = add_coverage(p0, "home", 20_000.0, 0.01)
    p2 = add_risk(p1, "high")
    p3 = with_meta(p2, agent="A-7")

    for name, p in [("p0", p0), ("p1", p1), ("p2", p2), ("p3", p3)]:
        print(
            f"{name}: coverages={len(p.coverages)} risks={sorted(p.risks)} "
            f"meta={dict(p.meta)} base={p.base_premium():.2f} "
            f"final={final_premium(p):.2f}"
        )
    print(
        "p0 is p3:",
        p0 is p3,
        "| p0 unchanged:",
        p0.coverages == (Coverage("car", 10_000.0, 0.05),),
    )
    print("cache:", final_premium.cache_info())
    index = index_by_policy((p0, p2))
    print(
        "as dict keys:",
        len(index),
        "policies ->",
        [round(v, 2) for v in index.values()],
    )
    try:
        p0.meta["source"] = "x"  # type: ignore[index]
    except TypeError as e:
        print("meta read-only:", e)


if __name__ == "__main__":
    main()
