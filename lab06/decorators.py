"""Параметризовані декоратори ЛР6: timed, retries, cached (TTL), authorized.

Усі зовнішні залежності (годинник, sleep, логер, джерело часу, сервіс перевірки
токена) інжектуються як Callable, тому тести детерміновані й без реальних затримок.
"""

from __future__ import annotations

import functools
import random
import threading
import time
from collections.abc import Callable
from typing import Any, Concatenate, Literal, ParamSpec, Protocol, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)

Key = tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]]


class AuthError(PermissionError):
    """Токен відсутній, порожній або не пройшов перевірку."""


class Decorator(Protocol):
    """Декоратор, що зберігає сигнатуру: Callable[P, R] -> Callable[P, R]."""

    def __call__(self, func: Callable[P, R], /) -> Callable[P, R]: ...


class CachedFn(Protocol[P, R_co]):
    """Обгортка з кешем: звичайний виклик плюс методи керування кешем."""

    __name__: str
    __doc__: str | None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    def cache_clear(self) -> None: ...

    def cache_invalidate(
        self, predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool]
    ) -> int: ...

    def cache_size(self) -> int: ...


class CacheDecorator(Protocol):
    """Декоратор, що повертає обгортку з методами кешу."""

    def __call__(self, func: Callable[P, R], /) -> CachedFn[P, R]: ...


class AuthDecorator(Protocol):
    """Декоратор, що додає токен першим позиційним аргументом."""

    def __call__(self, func: Callable[P, R], /) -> Callable[Concatenate[str, P], R]: ...


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None],
    clock: Callable[[], float] = time.perf_counter,
) -> Decorator:
    """Логує час виконання (навіть при винятку); годинник і логер інжектовані."""
    factor = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            t0 = clock()
            try:
                return func(*args, **kwargs)
            finally:
                logger(f"[timed] {name} took {(clock() - t0) * factor:.3f} {unit}")

        return wrapper

    return decorator


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = lambda _: None,
    rand: Callable[[], float] = random.random,
) -> Decorator:
    """Повторює виклик при зазначених винятках з експоненційним бекофом і джиттером."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == attempts:
                        logger(f"[retries] fail after {i} attempts: {e!r}")
                        raise
                    wait = delay * backoff ** (i - 1) + (
                        rand() * jitter if jitter else 0.0
                    )
                    logger(f"[retries] attempt {i} failed: {e!r}; sleeping {wait:.3f}s")
                    sleep(wait)
            raise AssertionError("unreachable")  # pragma: no cover

        return wrapper

    return decorator


def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Key:
    """Ключ кешу для хешованих аргументів: (args, відсортовані kwargs)."""
    return (args, tuple(sorted(kwargs.items())))


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> CacheDecorator:
    """Кеш з TTL; на обгортці є cache_clear, cache_invalidate, cache_size."""

    def decorator(func: Callable[P, R]) -> CachedFn[P, R]:
        cache: dict[Key, tuple[float | None, R]] = {}
        lock = threading.Lock()  # ponytail: один лок на функцію, достатньо для ЛР

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = make_key(args, kwargs)
            now = time_fn()
            with lock:
                if key in cache:
                    expiry, value = cache[key]
                    if expiry is None or now < expiry:
                        return value
                    del cache[key]
            value = func(*args, **kwargs)
            with lock:
                cache[key] = (None if ttl is None else now + ttl, value)
            return value

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_invalidate(
            predicate: Callable[[tuple[Any, ...], dict[str, Any]], bool],
        ) -> int:
            with lock:
                doomed = [k for k in cache if predicate(k[0], dict(k[1]))]
                for k in doomed:
                    del cache[k]
            return len(doomed)

        def cache_size() -> int:
            with lock:
                return len(cache)

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_invalidate = cache_invalidate  # type: ignore[attr-defined]
        wrapper.cache_size = cache_size  # type: ignore[attr-defined]
        return cast(CachedFn[P, R], wrapper)

    return decorator


def authorized(
    verify: Callable[[str], bool],
    *,
    logger: Callable[[str], None] = lambda _: None,
) -> AuthDecorator:
    """Варіант 13: обгортка вимагає токен ПЕРШИМ аргументом і пропускає виклик лише
    з валідним токеном; сама захищена функція токена не бачить.

    verify — інжектований сервіс перевірки (замикання над реєстром або віддалений
    сервіс, обгорнутий у @retries). Типізовано через Concatenate[str, P].
    """

    def decorator(func: Callable[P, R]) -> Callable[Concatenate[str, P], R]:
        @functools.wraps(func)
        def wrapper(token: str, /, *args: P.args, **kwargs: P.kwargs) -> R:
            if not token:
                logger(f"[auth] {func.__name__}: token missing")
                raise AuthError("token required")
            if not verify(token):
                logger(f"[auth] {func.__name__}: token rejected")
                raise AuthError("invalid token")
            logger(f"[auth] {func.__name__}: ok")
            return func(*args, **kwargs)

        return wrapper

    return decorator
