"""ADT платіжних операцій (варіант 13): frozen dataclass, Union, Literal, Protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias

Currency: TypeAlias = Literal["UAH", "USD", "EUR"]
CardNetwork: TypeAlias = Literal["visa", "mastercard"]


class PaymentSource(Protocol):
    """Структурний контракт: будь-що з сумою та валютою."""

    @property
    def amount(self) -> float: ...

    @property
    def currency(self) -> Currency: ...


@dataclass(frozen=True)
class CardPayment:
    amount: float
    currency: Currency
    network: CardNetwork
    last4: str


@dataclass(frozen=True)
class BankTransfer:
    amount: float
    currency: Currency
    iban: str
    urgent: bool = False


@dataclass(frozen=True)
class CashPayment:
    amount: float
    currency: Currency


@dataclass(frozen=True)
class Batch:
    """Вкладена структура: пакет платежів, що може містити інші пакети."""

    items: tuple[Payment, ...]
    label: str = ""


Payment: TypeAlias = CardPayment | BankTransfer | CashPayment | Batch
