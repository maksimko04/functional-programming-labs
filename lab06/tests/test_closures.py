from closures import (
    make_counter,
    make_logger,
    make_revocable_registry,
    make_token_registry,
)
from hypothesis import given
from hypothesis import strategies as st


def test_counter_keeps_state() -> None:
    c = make_counter(10)
    assert c() == 11
    assert c() == 12


def test_counters_are_independent() -> None:
    a, b = make_counter(), make_counter(100)
    assert [a(), a(), b()] == [1, 2, 101]


def test_logger_uses_injected_sink() -> None:
    lines: list[str] = []
    info = make_logger("INFO", lines.append)
    info("ready")
    assert lines == ["[INFO] ready"]


def test_token_registry() -> None:
    verify = make_token_registry(["abc", " xyz ", ""])
    assert verify("abc") and verify("xyz")
    assert not verify("") and not verify("nope")


def test_revocable_registry_shares_state() -> None:
    verify, revoke = make_revocable_registry(["t1", "t2"])
    assert verify("t1")
    revoke("t1")
    assert not verify("t1") and verify("t2")


@given(
    st.integers(min_value=-1000, max_value=1000), st.integers(min_value=0, max_value=50)
)
def test_property_counter_counts_calls(start: int, n: int) -> None:
    c = make_counter(start)
    assert [c() for _ in range(n)] == list(range(start + 1, start + n + 1))


@given(st.lists(st.text(min_size=1), max_size=10), st.text())
def test_property_registry_is_exact_membership(tokens: list[str], probe: str) -> None:
    verify = make_token_registry(tokens)
    assert verify(probe) == (probe in {t.strip() for t in tokens if t.strip()})
