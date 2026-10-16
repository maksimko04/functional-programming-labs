from dataclasses import FrozenInstanceError

import pytest
from core import (
    add_coverage,
    add_risk,
    final_premium,
    freeze,
    index_by_policy,
    with_meta,
)
from hypothesis import given
from hypothesis import strategies as st
from model import Coverage, Policy, make_meta, make_policy


def test_add_coverage_returns_new_policy(policy: Policy) -> None:
    before = (policy.coverages, policy.risks, dict(policy.meta))
    new = add_coverage(policy, "home", 20_000.0, 0.01)
    assert (policy.coverages, policy.risks, dict(policy.meta)) == before
    assert new is not policy
    assert len(new.coverages) == 3
    assert new.base_premium() == pytest.approx(policy.base_premium() + 200.0)


def test_add_risk_returns_new_policy(policy: Policy) -> None:
    new = add_risk(policy, "high")
    assert policy.risks == frozenset({"low"})
    assert new.risks == frozenset({"low", "high"})
    assert new.deactivate().active is False and policy.active is True


def test_frozen_fields_cannot_be_assigned(policy: Policy) -> None:
    with pytest.raises(FrozenInstanceError):
        policy.holder = "x"  # type: ignore[misc]


def test_meta_is_read_only(policy: Policy) -> None:
    with pytest.raises(TypeError):
        policy.meta["source"] = "changed"  # type: ignore[index]
    assert policy.meta["source"] == "web"


def test_make_meta_copies_source() -> None:
    raw = {"k": "v"}
    meta = make_meta(**raw)
    raw["k"] = "changed"
    assert meta["k"] == "v"


def test_with_meta_creates_new_mapping(policy: Policy) -> None:
    new = with_meta(policy, agent="B-1", channel="phone")
    assert dict(new.meta) == {"source": "web", "agent": "B-1", "channel": "phone"}
    assert dict(policy.meta) == {"source": "web", "agent": "A-7"}


def test_hashability_and_dict_key(policy: Policy) -> None:
    other = add_risk(policy, "high")
    assert len({policy, other, add_risk(policy, "high")}) == 2
    index = index_by_policy((policy, other))
    assert index[policy] == pytest.approx(540.0)
    assert index[other] == pytest.approx(600.0 * 0.9 * 1.5)
    assert set(index) == {policy, other}


def test_final_premium_and_cache(policy: Policy) -> None:
    final_premium.cache_clear()
    assert final_premium(policy) == pytest.approx((500.0 + 100.0) * 0.9)
    final_premium(policy)
    info = final_premium.cache_info()
    assert info.hits == 1 and info.misses == 1
    assert final_premium(add_risk(policy, "high")) == pytest.approx(600.0 * 0.9 * 1.5)


def test_freeze_deep() -> None:
    frozen = freeze({"a": [1, {2, 3}], "b": {"c": [4]}})
    with pytest.raises(TypeError):
        frozen["a"] = 0
    assert frozen["a"] == (1, frozenset({2, 3}))
    with pytest.raises(TypeError):
        frozen["b"]["c"] = 0
    assert frozen["b"]["c"] == (4,)


coverages_st = st.tuples(
    st.text(min_size=1, max_size=8),
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
    st.floats(min_value=0, max_value=1, allow_nan=False),
).map(lambda t: Coverage(*t))
policies_st = st.builds(
    make_policy,
    st.integers(min_value=1),
    st.text(min_size=1, max_size=10),
    st.tuples(coverages_st, coverages_st).map(tuple),
    st.frozensets(st.sampled_from(["low", "medium", "high"])),
)


@given(policies_st, coverages_st)
def test_property_add_coverage_pure(p: Policy, c: Coverage) -> None:
    before = (p.coverages, p.risks, dict(p.meta))
    new = p.add_coverage(c)
    assert (p.coverages, p.risks, dict(p.meta)) == before
    assert new.coverages == p.coverages + (c,)
    assert new.base_premium() == pytest.approx(p.base_premium() + c.premium())


@given(policies_st)
def test_property_hash_consistent_with_eq(p: Policy) -> None:
    twin = Policy(p.id, p.holder, p.coverages, p.risks, p.meta, p.active)
    assert twin == p and hash(twin) == hash(p)
    assert final_premium(p) == final_premium(twin)
