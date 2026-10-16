"""Замикання ЛР6: лічильник зі станом, логер з префіксом, реєстр допустимих токенів."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def make_counter(start: int = 0) -> Callable[[], int]:
    """Лічильник викликів: стан value живе в замиканні та змінюється через nonlocal."""
    value = start

    def inc() -> int:
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(prefix: str, sink: Callable[[str], None]) -> Callable[[str], None]:
    """Логер з інжектованим приймачем sink (без print у ядрі)."""
    return lambda msg: sink(f"[{prefix}] {msg}")


def make_token_registry(tokens: Iterable[str]) -> Callable[[str], bool]:
    """Замикання над незмінною множиною допустимих токенів: verify(token) -> bool."""
    allowed = frozenset(t.strip() for t in tokens if t.strip())
    return lambda token: token in allowed


def make_revocable_registry(
    tokens: Iterable[str],
) -> tuple[Callable[[str], bool], Callable[[str], None]]:
    """Реєстр з відкликанням: пара (verify, revoke) над спільним станом у замиканні."""
    allowed = set(tokens)

    def verify(token: str) -> bool:
        return token in allowed

    def revoke(token: str) -> None:
        allowed.discard(token)

    return verify, revoke
