"""Стартові імперативні фрагменти (з методички та за варіантом 13) для тестів."""

from typing import Any

TAX_RATE = 0.2  # глобальний стан
RISK_RATES = {"low": 0.9, "medium": 1.0, "high": 1.5}
DISCOUNT_PER_YEAR = 0.02
MAX_DISCOUNT = 0.3


def process_orders(
    orders: list[Any], min_total: float, discount: float
) -> dict[str, Any]:
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


def process_policies(policies: list[Any], min_premium: float) -> dict[str, Any]:
    valid: list[dict[str, Any]] = []
    total_premium = 0.0

    for p in policies:
        if not p["active"]:
            continue
        print("Processing policy:", p["id"])

        premium = p["base_premium"]
        if premium < min_premium:
            continue

        premium = premium * RISK_RATES[p["risk"]]
        discount = p["years"] * DISCOUNT_PER_YEAR
        if discount > MAX_DISCOUNT:
            discount = MAX_DISCOUNT
        premium = premium * (1 - discount)

        p["premium"] = premium
        valid.append(p)
        total_premium += premium

    return {"count": len(valid), "total_premium": total_premium, "policies": valid}
