from __future__ import annotations

from src.amm.pool import AMMPool
from src.utils.exceptions import InvalidSwapInputError, UnsupportedTokenError


def spot_price(pool: AMMPool, base_token: str, quote_token: str) -> float:
    """Compute the instantaneous spot price of base_token in quote_token units.

    Example:
        If base_token = ETH and quote_token = USDC,
        return how many USDC per 1 ETH.

    Args:
        pool: The AMM pool.
        base_token: Token being priced.
        quote_token: Token used as numeraire.

    Returns:
        Spot price base_token / quote_token.
    """
    if base_token == quote_token:
        raise ValueError("base_token and quote_token must be different.")

    if {base_token, quote_token} != {pool.token_x, pool.token_y}:
        raise UnsupportedTokenError(
            f"Pool contains {pool.token_x}/{pool.token_y}, "
            f"but requested {base_token}/{quote_token}."
        )

    if base_token == pool.token_x and quote_token == pool.token_y:
        return pool.reserve_y / pool.reserve_x

    return pool.reserve_x / pool.reserve_y


def mid_price(pool: AMMPool, token_in: str) -> float:
    """Return the pre-trade mid/spot price in input-token terms per output-token.

    Example:
        If token_in is USDC and the trade is USDC -> ETH,
        return USDC per ETH.

        If token_in is ETH and the trade is ETH -> USDC,
        return ETH per USDC.
    """
    if token_in == pool.token_x:
        return spot_price(pool, base_token=pool.token_y, quote_token=pool.token_x)
    if token_in == pool.token_y:
        return spot_price(pool, base_token=pool.token_x, quote_token=pool.token_y)

    raise UnsupportedTokenError(
        f"Token {token_in} is not supported by pool {pool.token_x}/{pool.token_y}."
    )


def get_amount_out(pool: AMMPool, token_in: str, amount_in: float) -> float:
    """Estimate output token amount for a constant-product swap.

    This function applies the standard AMM formula:
        amount_in_effective = amount_in * (1 - fee_rate)

    and then computes output while preserving the invariant.

    Args:
        pool: The AMM pool.
        token_in: Input token symbol.
        amount_in: Raw input amount before fee.

    Returns:
        Output token amount.
    """
    if amount_in <= 0:
        raise InvalidSwapInputError(
            f"Swap input must be positive. Got amount_in={amount_in}."
        )

    if token_in == pool.token_x:
        reserve_in = pool.reserve_x
        reserve_out = pool.reserve_y
    elif token_in == pool.token_y:
        reserve_in = pool.reserve_y
        reserve_out = pool.reserve_x
    else:
        raise UnsupportedTokenError(
            f"Token {token_in} is not supported by pool {pool.token_x}/{pool.token_y}."
        )

    amount_in_effective = amount_in * (1.0 - pool.fee_rate)
    numerator = amount_in_effective * reserve_out
    denominator = reserve_in + amount_in_effective
    amount_out = numerator / denominator

    return amount_out


def execution_price(pool: AMMPool, token_in: str, amount_in: float) -> float:
    """Compute realized execution price from an estimated swap.

    Returns:
        amount_in / amount_out in input-token terms per output-token unit.

    Example:
        If token_in is USDC and token_out is ETH,
        this returns USDC per ETH.
    """
    amount_out = get_amount_out(pool, token_in, amount_in)
    if amount_out <= 0:
        raise InvalidSwapInputError("Estimated output amount must be positive.")
    return amount_in / amount_out


def price_impact(pool: AMMPool, token_in: str, amount_in: float) -> float:
    """Measure relative execution deterioration versus pre-trade mid price.

    Defined as:
        (execution_price - mid_price) / mid_price

    Returns:
        Relative price impact as a fraction.
    """
    pre_trade_mid = mid_price(pool, token_in)
    realized_execution_price = execution_price(pool, token_in, amount_in)

    if pre_trade_mid <= 0:
        raise InvalidSwapInputError("Pre-trade mid price must be positive.")

    return (realized_execution_price - pre_trade_mid) / pre_trade_mid


def trade_size_ratio(pool: AMMPool, token_in: str, amount_in: float) -> float:
    """Measure trade size as a fraction of input-side liquidity."""
    if amount_in <= 0:
        raise InvalidSwapInputError(
            f"Swap input must be positive. Got amount_in={amount_in}."
        )

    reserve_in = pool.get_reserve(token_in)
    return amount_in / reserve_in