"""Порівняння часу: модель «до» (mutable) і «після» (immutable), --durations=5."""

from core import add_coverage, add_risk, final_premium
from model import Policy
from mutable_model import (
    add_coverage_inplace,
    add_risk_inplace,
    final_premium_dict,
    make_policy_dict,
)

N = 2_000


def test_mutable_before() -> None:
    p = make_policy_dict(1, "x")
    for i in range(N):
        add_coverage_inplace(p, f"c{i}", 100.0, 0.01)
    add_risk_inplace(p, "high")
    total = sum(final_premium_dict(p) for _ in range(N))
    assert total > 0


def test_immutable_after(policy: Policy) -> None:
    p = policy
    for i in range(N):
        p = add_coverage(p, f"c{i}", 100.0, 0.01)
    p = add_risk(p, "high")
    final_premium.cache_clear()
    total = sum(final_premium(p) for _ in range(N))
    assert total > 0
    assert final_premium.cache_info().hits == N - 1
