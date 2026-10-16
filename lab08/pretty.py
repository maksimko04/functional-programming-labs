"""Текстове представлення платежів через match/case."""

from __future__ import annotations

from typing import Protocol

from evaluator import fee
from model import BankTransfer, Batch, CardPayment, CashPayment, Payment


class Renders(Protocol):
    """Структурний контракт для будь-чого, що вміє відрендерити себе."""

    def render(self) -> str: ...


def describe(p: Payment, indent: int = 0) -> str:
    """Багаторядковий опис платежу; пакети рендеряться рекурсивно з відступом."""
    pad = "  " * indent
    match p:
        case CardPayment(amount=a, currency=c, network=n, last4=l4):
            return f"{pad}card {n} ****{l4}: {a:.2f} {c} (fee {fee(p):.2f})"
        case BankTransfer(amount=a, currency=c, iban=iban, urgent=True):
            return f"{pad}urgent transfer to {iban}: {a:.2f} {c} (fee {fee(p):.2f})"
        case BankTransfer(amount=a, currency=c, iban=iban):
            return f"{pad}transfer to {iban}: {a:.2f} {c} (fee {fee(p):.2f})"
        case CashPayment(amount=a, currency=c):
            return f"{pad}cash: {a:.2f} {c}"
        case Batch(items=items, label=label):
            head = f"{pad}batch {label or '(unnamed)'} [{len(items)}]"
            return "\n".join([head, *(describe(i, indent + 1) for i in items)])
