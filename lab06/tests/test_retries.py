import pytest
from decorators import retries


def test_retries_succeeds_on_third_attempt_without_sleep() -> None:
    calls = {"n": 0}
    slept: list[float] = []

    @retries(attempts=3, delay=0.5, backoff=2.0, sleep=slept.append)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3
    assert slept == [0.5, 1.0]  # експоненційний бекоф, без реального сну


def test_retries_reraises_after_last_attempt() -> None:
    logs: list[str] = []

    @retries(attempts=2, sleep=lambda _: None, logger=logs.append)
    def always_fails() -> None:
        raise ValueError("nope")

    with pytest.raises(ValueError):
        always_fails()
    assert any("fail after 2 attempts" in m for m in logs)


def test_retries_only_for_listed_exceptions() -> None:
    calls = {"n": 0}

    @retries(attempts=5, exceptions=(TimeoutError,), sleep=lambda _: None)
    def wrong_kind() -> None:
        calls["n"] += 1
        raise KeyError("not retried")

    with pytest.raises(KeyError):
        wrong_kind()
    assert calls["n"] == 1


def test_retries_jitter_is_deterministic_with_injected_rand() -> None:
    slept: list[float] = []
    calls = {"n": 0}

    @retries(attempts=2, delay=1.0, jitter=0.5, sleep=slept.append, rand=lambda: 0.5)
    def once_fails() -> int:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError
        return 1

    assert once_fails() == 1
    assert slept == [1.25]


def test_retries_invalid_attempts() -> None:
    with pytest.raises(ValueError):
        retries(attempts=0)
