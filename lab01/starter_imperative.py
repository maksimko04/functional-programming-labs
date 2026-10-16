"""Стартовий імперативний фрагмент (варіант 13, залишено для порівняння в тестах)."""

from typing import Any

RISK_RATES = {"low": 0.9, "medium": 1.0, "high": 1.5}  # глобальний стан
DISCOUNT_PER_YEAR = 0.02
MAX_DISCOUNT = 0.3


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
