"""Демо-запуск ЛР8: платежі (варіант 13) і базовий приклад з арифметичними виразами."""

from __future__ import annotations

from eval_ import eval_expr
from evaluator import statistics, total_with_fee
from expr import Add, Bin, Mul, Num, Num2, eval_expr2
from model import BankTransfer, Batch, CardPayment, CashPayment
from pretty import describe


def main() -> None:
    """Друкує опис пакета платежів, суми та статистику."""
    batch = Batch(
        label="order-42",
        items=(
            CardPayment(1000.0, "UAH", "visa", "4242"),
            BankTransfer(100.0, "USD", "UA123456", urgent=True),
            Batch(
                label="tips", items=(CashPayment(50.0, "UAH"), CashPayment(5.0, "EUR"))
            ),
        ),
    )
    print(describe(batch))
    print(f"total with fees: {total_with_fee(batch):.2f} UAH")
    print(f"total with fees: {total_with_fee(batch, 'USD'):.2f} USD")
    print("stats:", statistics((batch,)))

    ast = Mul(Add(Num(2), Num(3)), Num(4))
    print("(2 + 3) * 4 =", eval_expr(ast))
    print("Bin:", eval_expr2(Bin("+", Num2(2), Bin("*", Num2(3), Num2(4)))))


if __name__ == "__main__":
    main()
