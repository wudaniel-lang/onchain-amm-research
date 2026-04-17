from __future__ import annotations

from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.pricing import (
    execution_price,
    get_amount_out,
    mid_price,
    price_impact,
    spot_price,
    trade_size_ratio,
)
from src.utils.exceptions import InvalidSwapInputError, UnsupportedTokenError


@dataclass(frozen=True)
class SwapResult:
    """Container for swap execution result.

    This object is intentionally research-friendly: in addition to the raw swap
    output, it records pre/post-trade pricing state and diagnostic metrics such
    as price impact and trade size ratio.
    """

    token_in: str
    token_out: str
    amount_in: float
    amount_out: float
    fee_paid: float

    reserve_x_before: float
    reserve_y_before: float
    reserve_x_after: float
    reserve_y_after: float

    spot_price_before: float
    spot_price_after: float

    mid_price_before: float
    execution_price: float
    price_impact: float
    trade_size_ratio: float


def execute_swap(pool: AMMPool, token_in: str, amount_in: float) -> SwapResult:
    """Execute a swap on the AMM pool and update reserves in place.

    The pool applies fee on input amount, while the full input amount is added
    to the input reserve, matching standard fee-retaining constant-product AMM logic.

    Args:
        pool: AMM pool to mutate.
        token_in: Input token symbol.
        amount_in: Raw input amount.

    Returns:
        SwapResult containing execution details.
    """
    if amount_in <= 0:
        raise InvalidSwapInputError(
            f"Swap input must be positive. Got amount_in={amount_in}."
        )

    if token_in not in {pool.token_x, pool.token_y}:
        raise UnsupportedTokenError(
            f"Token {token_in} is not supported by pool {pool.token_x}/{pool.token_y}."
        )

    token_out = pool.get_other_token(token_in)

    reserve_x_before = pool.reserve_x
    reserve_y_before = pool.reserve_y

    spot_before = spot_price(pool, base_token=pool.token_x, quote_token=pool.token_y)
    pre_trade_mid = mid_price(pool, token_in)
    realized_execution_price = execution_price(pool, token_in, amount_in)
    relative_price_impact = price_impact(pool, token_in, amount_in)
    relative_trade_size = trade_size_ratio(pool, token_in, amount_in)

    amount_out = get_amount_out(pool, token_in, amount_in)
    fee_paid = amount_in * pool.fee_rate

    if token_in == pool.token_x:
        pool.reserve_x += amount_in
        pool.reserve_y -= amount_out
    else:
        pool.reserve_y += amount_in
        pool.reserve_x -= amount_out

    spot_after = spot_price(pool, base_token=pool.token_x, quote_token=pool.token_y)

    return SwapResult(
        token_in=token_in,
        token_out=token_out,
        amount_in=amount_in,
        amount_out=amount_out,
        fee_paid=fee_paid,
        reserve_x_before=reserve_x_before,
        reserve_y_before=reserve_y_before,
        reserve_x_after=pool.reserve_x,
        reserve_y_after=pool.reserve_y,
        spot_price_before=spot_before,
        spot_price_after=spot_after,
        mid_price_before=pre_trade_mid,
        execution_price=realized_execution_price,
        price_impact=relative_price_impact,
        trade_size_ratio=relative_trade_size,
    )