from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    """Simple spot position in ETH."""

    symbol: str = "ETH"
    quantity: float = 0.0

    def add(self, qty: float) -> None:
        """Increase or decrease position quantity."""
        self.quantity += qty