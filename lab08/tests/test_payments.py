from dataclasses import FrozenInstanceError

import pytest
from evaluator import (
    DEFAULT_RATES,
    convert,
    currency_of,
    fee,
    flatten,
    kind,
    statistics,
    total_with_fee,
)
from model import (
    BankTransfer,
    Batch,
    CardPayment,
    CashPayment,
    Currency,
    Payment,
    PaymentSource,
)
from pretty import describe

CARD = CardPayment(1000.0, "UAH", "visa", "4242")
MC = CardPayment(1000.0, "UAH", "mastercard", "1111")
TRANSFER = BankTransfer(100.0, "USD", "UA123456")
URGENT = BankTransfer(100.0, "USD", "UA123456", urgent=True)
CASH = CashPayment(50.0, "UAH")
BATCH = Batch(
    label="order", items=(CARD, URGENT, Batch(items=(CASH, CashPayment(5.0, "EUR"))))
)


def test_fee_per_kind() -> None:
    assert fee(CARD) == pytest.approx(20.0)
    assert fee(MC) == pytest.approx(18.0)
    assert fee(TRANSFER) == 5.0
    assert fee(URGENT) == 15.0
    assert fee(CASH) == 0.0


def test_fee_batch_is_recursive_sum() -> None:
    assert fee(BATCH) == pytest.approx(20.0 + 15.0 + 0.0 + 0.0)
    assert fee(Batch(items=())) == 0.0


def test_total_with_fee_and_conversion() -> None:
    assert total_with_fee(CARD) == pytest.approx(1020.0)
    assert total_with_fee(URGENT) == pytest.approx(115.0 * 41.5)
    assert total_with_fee(CASH, "USD") == pytest.approx(50.0 / 41.5)
    expected = 1020.0 + 115.0 * 41.5 + 50.0 + 5.0 * 45.0
    assert total_with_fee(BATCH) == pytest.approx(expected)
    assert total_with_fee(BATCH, "EUR") == pytest.approx(expected / 45.0)


def test_convert_with_custom_rates() -> None:
    rates: dict[Currency, float] = {"UAH": 1.0, "USD": 40.0, "EUR": 40.0}
    assert convert(10.0, "USD", "EUR", rates) == 10.0
    assert convert(1.0, "USD", "UAH", rates) == 40.0
    with pytest.raises(KeyError):
        convert(1.0, "USD", "GBP", rates)  # type: ignore[arg-type]


def test_negative_amount_rejected() -> None:
    with pytest.raises(ValueError):
        fee(CardPayment(-1.0, "UAH", "visa", "0000"))
    with pytest.raises(ValueError):
        total_with_fee(Batch(items=(CASH, CashPayment(-5.0, "UAH"))))


def test_nodes_are_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        CARD.amount = 1.0  # type: ignore[misc]
    assert CARD == CardPayment(1000.0, "UAH", "visa", "4242")
    assert len({CARD, CardPayment(1000.0, "UAH", "visa", "4242"), MC}) == 2


def test_flatten_and_kind() -> None:
    leaves = flatten(BATCH)
    assert leaves == (CARD, URGENT, CASH, CashPayment(5.0, "EUR"))
    assert [kind(p) for p in leaves] == ["card", "transfer", "cash", "cash"]
    assert kind(BATCH) == "batch" and flatten(CASH) == (CASH,)


def test_statistics() -> None:
    s = statistics((BATCH, MC))
    assert s["count"] == 5
    assert s["by_kind"] == {"card": 2, "transfer": 1, "cash": 2}
    assert s["fees_uah"] == pytest.approx(20.0 + 15.0 * 41.5 + 18.0)
    assert s["total_uah"] == pytest.approx(total_with_fee(BATCH) + 1018.0)
    assert statistics(()) == {
        "count": 0,
        "total_uah": 0.0,
        "fees_uah": 0.0,
        "by_kind": {},
    }


def test_describe_nested() -> None:
    text = describe(BATCH)
    assert text.splitlines() == [
        "batch order [3]",
        "  card visa ****4242: 1000.00 UAH (fee 20.00)",
        "  urgent transfer to UA123456: 100.00 USD (fee 15.00)",
        "  batch (unnamed) [2]",
        "    cash: 50.00 UAH",
        "    cash: 5.00 EUR",
    ]
    assert describe(TRANSFER) == "transfer to UA123456: 100.00 USD (fee 5.00)"


def test_protocol_and_currency() -> None:
    def total_of(src: PaymentSource) -> str:
        return f"{src.amount} {src.currency}"

    assert total_of(CARD) == "1000.0 UAH" and total_of(CASH) == "50.0 UAH"
    assert currency_of(URGENT) == "USD" and currency_of(BATCH) == "UAH"
    assert DEFAULT_RATES["UAH"] == 1.0
    p: Payment = CASH
    assert isinstance(p, CashPayment)
