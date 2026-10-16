"""Property-based тести (Hypothesis) для ADT платежів."""

from eval_ import eval_expr, render
from evaluator import fee, flatten, statistics, total_with_fee
from expr import Add, Expr, Mul, Num
from hypothesis import given
from hypothesis import strategies as st
from model import BankTransfer, Batch, CardPayment, CashPayment, Payment

amount = st.floats(min_value=0, max_value=1e5, allow_nan=False)
currency = st.sampled_from(["UAH", "USD", "EUR"])
leaf = st.one_of(
    st.builds(
        CardPayment,
        amount,
        currency,
        st.sampled_from(["visa", "mastercard"]),
        st.just("0000"),
    ),
    st.builds(BankTransfer, amount, currency, st.just("UA1"), st.booleans()),
    st.builds(CashPayment, amount, currency),
)
payment = st.recursive(
    leaf,
    lambda inner: st.builds(Batch, st.lists(inner, max_size=4).map(tuple)),
    max_leaves=12,
)


@given(payment)
def test_batch_total_equals_sum_of_leaves(p: Payment) -> None:
    leaves = flatten(p)
    assert abs(total_with_fee(p) - sum(total_with_fee(x) for x in leaves)) < 1e-6
    assert abs(fee(p) - sum(fee(x) for x in leaves)) < 1e-6


@given(st.lists(payment, max_size=5).map(tuple))
def test_statistics_count_matches_flatten(ps: tuple[Payment, ...]) -> None:
    s = statistics(ps)
    assert s["count"] == sum(len(flatten(p)) for p in ps) == sum(s["by_kind"].values())
    assert s["total_uah"] >= s["fees_uah"] >= 0.0


expr = st.recursive(
    st.builds(Num, st.integers(min_value=0, max_value=9)),
    lambda inner: st.one_of(st.builds(Add, inner, inner), st.builds(Mul, inner, inner)),
    max_leaves=6,
)


@given(expr)
def test_render_is_evaluable_python(e: Expr) -> None:
    try:
        value = eval_expr(e)
    except ValueError:
        return
    assert value == eval(render(e))  # noqa: S307 — рядок згенеровано нашим render
