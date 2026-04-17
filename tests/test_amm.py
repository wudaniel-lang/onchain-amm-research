from __future__ import annotations

import math

import pytest

from src.amm.pool import AMMPool
from src.amm.pricing import (
    execution_price,
    get_amount_out,
    mid_price,
    price_impact,
    spot_price,
    trade_size_ratio,
)
from src.amm.swap import execute_swap
from src.utils.exceptions import (
    InvalidReserveError,
    InvalidSwapInputError,
    UnsupportedTokenError,
)


@pytest.fixture
def sample_pool() -> AMMPool:
    return AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )


def test_pool_initialization(sample_pool: AMMPool) -> None:
    assert sample_pool.token_x == "ETH"
    assert sample_pool.token_y == "USDC"
    assert sample_pool.reserve_x == 100.0
    assert sample_pool.reserve_y == 200000.0
    assert sample_pool.fee_rate == 0.003


def test_invalid_pool_reserve_raises() -> None:
    with pytest.raises(InvalidReserveError):
        AMMPool(
            token_x="ETH",
            token_y="USDC",
            reserve_x=0.0,
            reserve_y=1000.0,
            fee_rate=0.003,
        )


def test_spot_price(sample_pool: AMMPool) -> None:
    eth_price = spot_price(sample_pool, base_token="ETH", quote_token="USDC")
    usdc_price = spot_price(sample_pool, base_token="USDC", quote_token="ETH")

    assert eth_price == 2000.0
    assert math.isclose(usdc_price, 1 / 2000.0, rel_tol=1e-12)


def test_mid_price_for_usdc_to_eth_trade(sample_pool: AMMPool) -> None:
    assert mid_price(sample_pool, token_in="USDC") == 2000.0


def test_get_amount_out_positive(sample_pool: AMMPool) -> None:
    amount_out = get_amount_out(sample_pool, token_in="USDC", amount_in=1000.0)
    assert amount_out > 0.0
    assert amount_out < sample_pool.reserve_x


def test_get_amount_out_invalid_input_raises(sample_pool: AMMPool) -> None:
    with pytest.raises(InvalidSwapInputError):
        get_amount_out(sample_pool, token_in="USDC", amount_in=0.0)


def test_get_amount_out_unsupported_token_raises(sample_pool: AMMPool) -> None:
    with pytest.raises(UnsupportedTokenError):
        get_amount_out(sample_pool, token_in="BTC", amount_in=1000.0)


def test_execution_price_worse_than_initial_spot_for_buying_eth(sample_pool: AMMPool) -> None:
    initial_spot = spot_price(sample_pool, base_token="ETH", quote_token="USDC")
    realized_price = execution_price(sample_pool, token_in="USDC", amount_in=5000.0)

    assert realized_price > initial_spot


def test_price_impact_is_positive(sample_pool: AMMPool) -> None:
    impact = price_impact(sample_pool, token_in="USDC", amount_in=1000.0)
    assert impact > 0.0


def test_larger_trade_has_larger_price_impact(sample_pool: AMMPool) -> None:
    small_impact = price_impact(sample_pool, token_in="USDC", amount_in=1000.0)
    large_impact = price_impact(sample_pool, token_in="USDC", amount_in=10000.0)

    assert large_impact > small_impact


def test_trade_size_ratio(sample_pool: AMMPool) -> None:
    ratio = trade_size_ratio(sample_pool, token_in="USDC", amount_in=1000.0)
    assert math.isclose(ratio, 1000.0 / 200000.0, rel_tol=1e-12)


def test_execute_swap_updates_reserves(sample_pool: AMMPool) -> None:
    old_x = sample_pool.reserve_x
    old_y = sample_pool.reserve_y

    result = execute_swap(sample_pool, token_in="USDC", amount_in=1000.0)

    assert result.amount_out > 0.0
    assert sample_pool.reserve_y > old_y
    assert sample_pool.reserve_x < old_x


def test_execute_swap_fee_paid(sample_pool: AMMPool) -> None:
    result = execute_swap(sample_pool, token_in="USDC", amount_in=1000.0)
    assert math.isclose(result.fee_paid, 3.0, rel_tol=1e-12)


def test_execute_swap_increases_invariant_due_to_fee(sample_pool: AMMPool) -> None:
    k_before = sample_pool.invariant
    execute_swap(sample_pool, token_in="USDC", amount_in=1000.0)
    k_after = sample_pool.invariant

    assert k_after > k_before


def test_swap_result_contains_research_metrics(sample_pool: AMMPool) -> None:
    result = execute_swap(sample_pool, token_in="USDC", amount_in=1000.0)

    assert result.mid_price_before > 0.0
    assert result.execution_price > result.mid_price_before
    assert result.price_impact > 0.0
    assert result.trade_size_ratio > 0.0


def test_execute_swap_invalid_amount_raises(sample_pool: AMMPool) -> None:
    with pytest.raises(InvalidSwapInputError):
        execute_swap(sample_pool, token_in="USDC", amount_in=-1.0)


def test_execute_swap_unsupported_token_raises(sample_pool: AMMPool) -> None:
    with pytest.raises(UnsupportedTokenError):
        execute_swap(sample_pool, token_in="BTC", amount_in=100.0)