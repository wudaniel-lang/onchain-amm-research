from __future__ import annotations

from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.pricing import spot_price
from src.portfolio.portfolio import Portfolio
from src.strategies.base import BaseStrategy
from src.types.common import MarketSnapshot, Side, Signal


@dataclass
class SimpleArbitrageStrategy(BaseStrategy):
    """A minimal external-price-vs-AMM arbitrage strategy.

    Logic:
    - If external_price is sufficiently above AMM price, buy ETH from AMM using USDC.
    - If external_price is sufficiently below AMM price, sell ETH into AMM.
    - Otherwise hold.

    Notes:
    - This is deliberately simple for Day 2.
    - It serves as a research baseline, not a production strategy.
    """

    buy_threshold_bps: float = 50.0
    sell_threshold_bps: float = 50.0
    buy_size_usdc: float = 1000.0
    sell_size_eth: float = 0.5

    def generate_signal(
        self,
        market: MarketSnapshot,
        pool: AMMPool,
        portfolio: Portfolio,
    ) -> Signal:
        amm_price = spot_price(pool, base_token="ETH", quote_token="USDC")
        diff_ratio = (market.external_price - amm_price) / amm_price
        diff_bps = diff_ratio * 10_000.0

        if diff_bps >= self.buy_threshold_bps:
            affordable_size = min(self.buy_size_usdc, max(portfolio.cash_usdc, 0.0))
            if affordable_size > 0:
                return Signal(
                    timestamp=market.timestamp,
                    side=Side.BUY,
                    size=affordable_size,
                    reason=(
                        f"External price above AMM by {diff_bps:.2f} bps; "
                        f"buy ETH from AMM."
                    ),
                )

        if diff_bps <= -self.sell_threshold_bps:
            sell_size = min(self.sell_size_eth, max(portfolio.eth_position.quantity, 0.0))
            if sell_size > 0:
                return Signal(
                    timestamp=market.timestamp,
                    side=Side.SELL,
                    size=sell_size,
                    reason=(
                        f"External price below AMM by {abs(diff_bps):.2f} bps; "
                        f"sell ETH into AMM."
                    ),
                )

        return Signal(
            timestamp=market.timestamp,
            side=Side.HOLD,
            size=0.0,
            reason="No actionable price dislocation.",
        )