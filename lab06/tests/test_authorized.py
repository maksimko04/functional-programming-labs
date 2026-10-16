import pytest
from closures import make_counter, make_token_registry
from decorators import AuthError, authorized, cached, retries, timed


def test_authorized_allows_valid_token_and_hides_it() -> None:
    logs: list[str] = []

    @authorized(make_token_registry(["good"]), logger=logs.append)
    def secret(x: int) -> int:
        """Захищена."""
        return x + 1

    assert secret("good", 1) == 2
    assert logs == ["[auth] secret: ok"]
    assert secret.__name__ == "secret" and secret.__doc__ == "Захищена."


@pytest.mark.parametrize("bad", ["", "wrong", "GOOD"])
def test_authorized_rejects_bad_tokens(bad: str) -> None:
    calls = make_counter()

    @authorized(make_token_registry(["good"]))
    def secret() -> int:
        return calls()

    with pytest.raises(AuthError):
        secret(bad)
    assert calls() == 1  # захищена функція не викликалась


def test_authorized_error_messages() -> None:
    @authorized(lambda t: t == "k")
    def secret() -> str:
        return "x"

    with pytest.raises(AuthError, match="token required"):
        secret("")
    with pytest.raises(AuthError, match="invalid token"):
        secret("other")
    assert secret("k") == "x"


def test_verify_service_with_retries_is_injected() -> None:
    attempts = make_counter()
    slept: list[float] = []

    @retries(attempts=3, delay=0.1, sleep=slept.append)
    def remote_verify(token: str) -> bool:
        if attempts() < 3:
            raise ConnectionError("down")
        return token == "ok"

    @authorized(remote_verify)
    def secret() -> str:
        return "data"

    assert secret("ok") == "data"
    assert slept == [0.1, 0.1]
    with pytest.raises(AuthError):
        secret("bad")


def test_decorator_order_cache_inside_auth() -> None:
    hits = make_counter()
    logs: list[str] = []
    tick = make_counter()

    @cached()
    def compute(x: int) -> int:
        hits()
        return x * 10

    guarded = timed("op", logger=logs.append, clock=lambda: float(tick()))(
        authorized(make_token_registry(["t"]))(compute)
    )
    assert guarded("t", 2) == 20
    assert guarded("t", 2) == 20
    assert compute.cache_size() == 1 and hits() == 2  # кеш-хіт: обчислено один раз
    with pytest.raises(AuthError):
        guarded("no", 2)  # кеш не обходить авторизацію
    assert len(logs) == 3  # timed спрацював на кожен виклик, включно з відмовою
