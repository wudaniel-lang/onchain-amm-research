from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Side(str, Enum):
    """Trading side / intention."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class MarketSnapshot:
    """Minimal market state used by strategy and backtest.

    Attributes:
        timestamp: Logical time index or label.
        external_price: Reference market price in USDC per ETH.
    """

    timestamp: str
    external_price: float


@dataclass(frozen=True)
class Signal:
    """Strategy output signal.

    Attributes:
        timestamp: Time label.
        side: BUY / SELL / HOLD.
        size: Trade amount in the input token denomination.
        reason: Human-readable explanation for debugging / research logs.
    """

    timestamp: str
    side: Side
    size: float
    reason: str