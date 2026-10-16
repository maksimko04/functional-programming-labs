"""Property-based тести (Hypothesis) для чистого ядра."""

from copy import deepcopy

from core import Policy, Report, process_policies_pure
from hypothesis import given
from hypothesis import strategies as st

RATES = {"low": 0.9, "medium": 1.0, "high": 1.5}


def run(items: list[Policy]) -> Report:
    return process_policies_pure(
        items,
        min_premium=0.0,
        risk_rates=RATES,
        discount_per_year=0.02,
        max_discount=0.3,
    )


policies = st.lists(
    st.fixed_dictionaries(
        {
            "id": st.integers(min_value=1),
            "base_premium": st.floats(min_value=0, max_value=1e6, allow_nan=False),
            "risk": st.sampled_from(["low", "medium", "high"]),
            "years": st.integers(min_value=0, max_value=60),
            "active": st.booleans(),
        }
    ),
    max_size=20,
)


@given(policies)
def test_property_referential_transparency(items: list[Policy]) -> None:
    assert run(items) == run(items)


@given(policies)
def test_property_no_mutation(items: list[Policy]) -> None:
    original = deepcopy(items)
    process_policies_pure(
        items,
        min_premium=0.0,
        risk_rates=RATES,
        discount_per_year=0.02,
        max_discount=0.3,
    )
    assert items == original


@given(policies)
def test_property_total_is_sum_and_only_active(items: list[Policy]) -> None:
    result = process_policies_pure(
        items,
        min_premium=0.0,
        risk_rates=RATES,
        discount_per_year=0.02,
        max_discount=0.3,
    )
    assert result["count"] == sum(1 for p in items if p["active"])
    assert result["total_premium"] == sum(p["premium"] for p in result["policies"])
    assert all(p["premium"] <= p["base_premium"] * 1.5 for p in result["policies"])
