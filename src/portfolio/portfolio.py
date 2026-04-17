from __future__ import annotations

from dataclasses import dataclass, field

from src.execution.engine import ExecutionResult
from src.portfolio.position import Position


@dataclass
class Portfolio:
    """Minimal portfolio for Day 2.

    Attributes:
        cash_usdc: Cash balance.
        eth_position: ETH spot position.
        gas_spent_usdc: Cumulative gas spending.
        trade_count: Number of executed trades.
    """

    cash_usdc: float
    eth_position: Position = field(default_factory=Position)
    gas_spent_usdc: float = 0.0
    trade_count: int = 0

    def apply_execution(self, result: ExecutionResult) -> None:
        """Apply execution result to portfolio state."""
        self.cash_usdc += result.net_cash_flow_usdc
        self.eth_position.add(result.net_eth_flow)
        self.gas_spent_usdc += result.gas_cost_usdc
        self.trade_count += 1

    def equity(self, external_price: float) -> float:
        """Compute marked-to-market portfolio equity in USDC."""
        return self.cash_usdc + self.eth_position.quantity * external_price

    def snapshot(self, external_price: float) -> dict[str, float]:
        """Return a flat snapshot for logging / analysis."""
        return {
            "cash_usdc": self.cash_usdc,
            "eth_qty": self.eth_position.quantity,
            "gas_spent_usdc": self.gas_spent_usdc,
            "trade_count": float(self.trade_count),
            "equity_usdc": self.equity(external_price),
        }

    def summary(self, external_price: float) -> dict[str, float]:
        """Return a compact summary for experiment reporting."""
        return {
            "cash_usdc": self.cash_usdc,
            "eth_qty": self.eth_position.quantity,
            "equity_usdc": self.equity(external_price),
            "gas_spent_usdc": self.gas_spent_usdc,
            "trade_count": float(self.trade_count),
        }