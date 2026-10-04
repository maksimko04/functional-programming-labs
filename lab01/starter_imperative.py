"""Стартовий імперативний фрагмент із завдання (залишено для порівняння в тестах)."""

from typing import Any

TAX_RATE = 0.2


def process_orders(orders: list[Any], min_total: float, discount: float) -> dict[str, Any]:
    valid: list[dict[str, Any]] = []
    total_revenue = 0.0

    for o in orders:
        if not o["paid"]:
            continue
        print("Processing order:", o["id"])

        order_total = 0.0
        for it in o["items"]:
            order_total += it["price"] * it["qty"]
        if order_total < min_total:
            continue

        order_total = order_total * (1 - discount)
        order_total = order_total * (1 + TAX_RATE)

        o["total"] = order_total
        valid.append(o)
        total_revenue += order_total

    return {"count": len(valid), "revenue": total_revenue, "orders": valid}
