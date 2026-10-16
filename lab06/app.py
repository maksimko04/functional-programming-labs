"""Демо ЛР6: захищена сервісна функція з контролем доступу за токеном (варіант 13).

Жодних реальних затримок: sleep, clock і сервіс перевірки токена підмінені.
"""

from __future__ import annotations

from closures import make_counter, make_logger, make_token_registry
from decorators import AuthError, authorized, cached, retries, timed

log = make_logger("app", print)
ticks = make_counter()
fake_clock = lambda: ticks() * 0.001  # noqa: E731  — детермінований «годинник»
fake_sleep = lambda s: log(f"(sleep {s:.3f}s skipped)")  # noqa: E731

local_verify = make_token_registry(["alpha-1", "beta-2"])
flaky_calls = make_counter()


@retries(attempts=3, delay=0.1, backoff=2.0, sleep=fake_sleep, logger=log)
def remote_verify(token: str) -> bool:
    """Нестабільний сервіс перевірки: перші два виклики падають, далі відповідає."""
    if flaky_calls() < 3:
        raise ConnectionError("verify service unavailable")
    return local_verify(token)


@cached(ttl=60.0, time_fn=fake_clock)
def compute_balance(account_id: int) -> float:
    """Дорога операція з кешем (внутрішній шар, без контролю доступу)."""
    log(f"computing balance for {account_id}")
    return 100.0 * account_id


# порядок знизу вгору: кеш -> авторизація -> таймінг; кеш-хіт усе одно вимагає токен
account_balance = timed("balance", logger=log, clock=fake_clock)(
    authorized(remote_verify, logger=log)(compute_balance)
)


def main() -> None:
    """Показує успішний виклик, кеш-хіт і відмову за поганим токеном."""
    print("balance:", account_balance("alpha-1", 7))
    print("balance again (cache hit):", account_balance("beta-2", 7))
    print("cache size:", compute_balance.cache_size())
    for bad in ("", "nope"):
        try:
            account_balance(bad, 7)
        except AuthError as e:
            print("denied:", e)


if __name__ == "__main__":
    main()
