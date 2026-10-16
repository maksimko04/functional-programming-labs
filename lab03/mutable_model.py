"""Мутабельна модель «до» переходу на immutable — лише для порівняння в тестах."""

from __future__ import annotations

from typing import Any

RISK_FACTORS = {"low": 0.9, "medium": 1.0, "high": 1.5}


def make_policy_dict(id: int, holder: str) -> dict[str, Any]:
    """Поліс як звичайний dict зі списком, множиною і вкладеним dict."""
    return {
        "id": id,
        "holder": holder,
        "coverages": [],
        "risks": set(),
        "meta": {},
        "active": True,
    }


def add_coverage_inplace(
    policy: dict[str, Any], name: str, amount: float, rate: float
) -> None:
    """Мутує список покриттів."""
    policy["coverages"].append({"name": name, "amount": amount, "rate": rate})


def add_risk_inplace(policy: dict[str, Any], risk: str) -> None:
    """Мутує множину ризиків."""
    policy["risks"].add(risk)


def final_premium_dict(policy: dict[str, Any]) -> float:
    """Премія без кешу: щоразу перераховується."""
    base = sum(c["amount"] * c["rate"] for c in policy["coverages"])
    factor = 1.0
    for r in policy["risks"]:
        factor *= RISK_FACTORS[r]
    return float(base * factor)
