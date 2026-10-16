from copy import deepcopy

import pytest
from app import render_report
from core import (
    Policy,
    Report,
    compose,
    final_premium,
    make_multiplier,
    make_policy_processor,
    min_premium_filter,
    process_policies_pure,
    stamp_total,
    table_risk,
    with_premium,
    years_discount,
)
from starter_imperative import process_policies

RATES = {"low": 0.9, "medium": 1.0, "high": 1.5}


def run(policies: list[Policy]) -> Report:
    return process_policies_pure(
        policies,
        min_premium=500.0,
        risk_rates=RATES,
        discount_per_year=0.02,
        max_discount=0.3,
    )


def test_referential_transparency(sample_policies: list[Policy]) -> None:
    r1 = run(sample_policies)
    r2 = run(sample_policies)
    assert r1 == r2


def test_no_mutation(sample_policies: list[Policy]) -> None:
    original = deepcopy(sample_policies)
    process_policies_pure(
        sample_policies,
        min_premium=0,
        risk_rates=RATES,
        discount_per_year=0.0,
        max_discount=0.0,
    )
    assert sample_policies == original


def test_matches_imperative(sample_policies: list[Policy]) -> None:
    expected = process_policies(deepcopy(sample_policies), 500)
    assert run(sample_policies) == expected


def test_filters_inactive_and_small(sample_policies: list[Policy]) -> None:
    result = run(sample_policies)
    assert [p["id"] for p in result["policies"]] == [1, 4, 5]
    assert result["count"] == 3
    assert result["total_premium"] == pytest.approx(
        1000 * 0.9 * 0.9 + 1500 * 1.5 * 0.7 + 500 * 1.0 * 0.98
    )


def test_final_premium() -> None:
    assert final_premium(1000.0, 1.5, 0.1) == pytest.approx(1350.0)
    assert final_premium(0.0, 2.0, 0.5) == 0.0


def test_with_premium_returns_new_dict() -> None:
    policy: Policy = {
        "id": 1,
        "base_premium": 100.0,
        "risk": "low",
        "years": 0,
        "active": True,
    }
    new = with_premium(policy, 42.0)
    assert new == {**policy, "premium": 42.0}
    assert "premium" not in policy
    assert new is not policy


def test_callable_policies(sample_policies: list[Policy]) -> None:
    process = make_policy_processor(
        accept=lambda base: base >= 1000,
        risk_factor=lambda risk: 2.0 if risk == "high" else 1.0,
        loyalty_discount=lambda years: 0.5 if years >= 10 else 0.0,
    )
    result = process(sample_policies)
    assert [p["id"] for p in result["policies"]] == [1, 4]
    assert result["total_premium"] == pytest.approx(1000 * 1.0 + 1500 * 2.0 * 0.5)


def test_policy_factories() -> None:
    assert min_premium_filter(500)(499.9) is False
    assert min_premium_filter(500)(500) is True
    assert table_risk(RATES)("high") == 1.5
    assert table_risk(RATES, default=1.0)("unknown") == 1.0
    assert years_discount(0.02, 0.3)(5) == pytest.approx(0.1)
    assert years_discount(0.02, 0.3)(50) == 0.3


def test_compose_and_multiplier() -> None:
    discount_for = compose(years_discount(0.02, 0.3), make_multiplier(2))
    assert discount_for(5) == pytest.approx(0.2)
    assert make_multiplier(3)(7) == 21
    assert compose(make_multiplier(2), make_multiplier(5))(1) == 10


def test_stamp_total_uses_injected_clock() -> None:
    assert stamp_total(10.0, lambda: 123.0) == (10.0, 123.0)


def test_render_report(sample_policies: list[Policy]) -> None:
    text = render_report(run(sample_policies))
    assert text.splitlines() == [
        "Policy: 1 premium: 810.00",
        "Policy: 4 premium: 1575.00",
        "Policy: 5 premium: 490.00",
        "Count: 3",
        "Total: 2875.00",
    ]
