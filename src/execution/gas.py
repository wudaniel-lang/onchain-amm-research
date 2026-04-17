from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GasModel:
    """Simple fixed gas cost model.

    Attributes:
        fixed_cost_usdc: Flat execution cost charged per trade.
    """

    fixed_cost_usdc: float = 5.0

    def estimate_cost(self) -> float:
        """Return fixed gas cost in USDC."""
        return self.fixed_cost_usdc