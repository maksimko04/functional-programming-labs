"""Чисті операції над ADT платежів через match/case (варіант 13)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypedDict

from model import BankTransfer, Batch, CardPayment, CashPayment, Currency, Payment

Rates = Mapping[Currency, float]

DEFAULT_RATES: Rates = {"UAH": 1.0, "USD": 41.5, "EUR": 45.0}
"""Курс до гривні; передається явно, щоб ядро лишалося чистим."""


class Stats(TypedDict):
    count: int
    total_uah: float
    fees_uah: float
    by_kind: dict[str, int]


def _check_amount(amount: float) -> float:
    if amount < 0:
        raise ValueError(f"negative amount: {amount}")
    return amount


def fee(p: Payment) -> float:
    """Комісія у валюті платежу: visa 2 %, mastercard 1.8 %, переказ 5 (+10 urgent)."""
    match p:
        case CardPayment(amount=a, network="visa"):
            return _check_amount(a) * 0.02
        case CardPayment(amount=a):
            return _check_amount(a) * 0.018
        case BankTransfer(amount=a, urgent=urgent):
            _check_amount(a)
            return 5.0 + (10.0 if urgent else 0.0)
        case CashPayment(amount=a):
            _check_amount(a)
            return 0.0
        case Batch(items=items):
            return sum(fee(i) for i in items)


def convert(
    amount: float, src: Currency, dst: Currency, rates: Rates = DEFAULT_RATES
) -> float:
    """Конвертація через гривню за явною таблицею курсів."""
    if src not in rates or dst not in rates:
        raise KeyError(f"unknown currency: {src if src not in rates else dst}")
    return amount * rates[src] / rates[dst]


def total_with_fee(
    p: Payment, currency: Currency = "UAH", rates: Rates = DEFAULT_RATES
) -> float:
    """Сума плюс комісія, зведена до заданої валюти (рекурсивно для Batch)."""
    match p:
        case Batch(items=items):
            return sum(total_with_fee(i, currency, rates) for i in items)
        case (
            CardPayment(amount=a, currency=c)
            | BankTransfer(amount=a, currency=c)
            | CashPayment(amount=a, currency=c)
        ):
            return convert(_check_amount(a) + fee(p), c, currency, rates)


def kind(p: Payment) -> str:
    """Назва виду платежу для статистики."""
    match p:
        case CardPayment():
            return "card"
        case BankTransfer():
            return "transfer"
        case CashPayment():
            return "cash"
        case Batch():
            return "batch"


def flatten(p: Payment) -> tuple[Payment, ...]:
    """Усі листові платежі пакета у порядку обходу (новий кортеж)."""
    match p:
        case Batch(items=items):
            return tuple(leaf for i in items for leaf in flatten(i))
        case _:
            return (p,)


def statistics(payments: tuple[Payment, ...], rates: Rates = DEFAULT_RATES) -> Stats:
    """Агрегат: кількість листових платежів, суми у гривні, розподіл за видами."""
    leaves = tuple(leaf for p in payments for leaf in flatten(p))
    by_kind: dict[str, int] = {}
    for leaf in leaves:
        by_kind = {**by_kind, kind(leaf): by_kind.get(kind(leaf), 0) + 1}
    return {
        "count": len(leaves),
        "total_uah": sum(total_with_fee(leaf, "UAH", rates) for leaf in leaves),
        "fees_uah": sum(
            convert(fee(leaf), currency_of(leaf), "UAH", rates) for leaf in leaves
        ),
        "by_kind": by_kind,
    }


def currency_of(p: Payment) -> Currency:
    """Валюта листового платежу; для Batch — UAH (сума вже зведена)."""
    match p:
        case (
            CardPayment(currency=c) | BankTransfer(currency=c) | CashPayment(currency=c)
        ):
            return c
        case Batch():
            return "UAH"
