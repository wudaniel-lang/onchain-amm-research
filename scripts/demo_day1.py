from __future__ import annotations

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


def print_section(title: str) -> None:
    """Print a formatted section title."""
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    """Run a user-friendly Day 1 AMM demonstration.

    This script is intended for:
    - quick sanity checks
    - in-class demo
    - README examples
    - explaining Day 1 deliverables
    """
    pool = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )

    amount_in = 5000.0
    token_in = "USDC"

    print_section("DAY 1 DEMO: AMM INITIALIZATION")
    print(f"Pool pair: {pool.token_x}/{pool.token_y}")
    print(f"Initial reserves: {pool.token_x}={pool.reserve_x:.6f}, {pool.token_y}={pool.reserve_y:.6f}")
    print(f"Fee rate: {pool.fee_rate:.4%}")
    print(f"Initial invariant k: {pool.invariant:.6f}")

    print_section("PRE-TRADE PRICING")
    spot = spot_price(pool, base_token="ETH", quote_token="USDC")
    mid = mid_price(pool, token_in=token_in)
    amount_out = get_amount_out(pool, token_in=token_in, amount_in=amount_in)
    exec_px = execution_price(pool, token_in=token_in, amount_in=amount_in)
    impact = price_impact(pool, token_in=token_in, amount_in=amount_in)
    size_ratio = trade_size_ratio(pool, token_in=token_in, amount_in=amount_in)

    print(f"Spot price (ETH in USDC): {spot:.6f}")
    print(f"Mid price before trade: {mid:.6f}")
    print(f"Quoted amount out: {amount_out:.6f} ETH")
    print(f"Execution price: {exec_px:.6f} USDC/ETH")
    print(f"Price impact: {impact:.6%}")
    print(f"Trade size ratio: {size_ratio:.6%}")

    print_section("SWAP EXECUTION")
    result = execute_swap(pool, token_in=token_in, amount_in=amount_in)

    print(f"Trade: {result.amount_in:.6f} {result.token_in} -> {result.amount_out:.6f} {result.token_out}")
    print(f"Fee paid: {result.fee_paid:.6f} {result.token_in}")
    print(f"Spot before: {result.spot_price_before:.6f}")
    print(f"Spot after: {result.spot_price_after:.6f}")
    print(f"Mid before: {result.mid_price_before:.6f}")
    print(f"Execution price: {result.execution_price:.6f}")
    print(f"Price impact: {result.price_impact:.6%}")
    print(f"Trade size ratio: {result.trade_size_ratio:.6%}")

    print_section("POST-TRADE POOL STATE")
    print(f"Updated reserves: {pool.token_x}={pool.reserve_x:.6f}, {pool.token_y}={pool.reserve_y:.6f}")
    print(f"Updated invariant k: {pool.invariant:.6f}")

    print_section("DAY 1 TAKEAWAYS")
    print("1. The AMM correctly prices swaps under a constant-product mechanism.")
    print("2. Execution price is worse than the pre-trade spot/mid price due to slippage and fees.")
    print("3. Larger trades consume more liquidity and create higher price impact.")
    print("4. The module is now ready to support Day 2 execution and portfolio layers.")


if __name__ == "__main__":
    main()