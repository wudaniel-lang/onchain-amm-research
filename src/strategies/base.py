from __future__ import annotations

from abc import ABC, abstractmethod

from src.amm.pool import AMMPool
from src.portfolio.portfolio import Portfolio
from src.types.common import MarketSnapshot, Signal


class BaseStrategy(ABC):
    """Abstract strategy interface."""

    @abstractmethod
    def generate_signal(
        self,
        market: MarketSnapshot,
        pool: AMMPool,
        portfolio: Portfolio,
    ) -> Signal:
        """Generate a trading signal for the given market state."""
        raise NotImplementedError