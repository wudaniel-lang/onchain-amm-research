from __future__ import annotations

from dataclasses import dataclass

from src.utils.exceptions import InvalidReserveError


@dataclass
class AMMPool:
    """Represents a constant-product AMM liquidity pool.

    This class stores the mutable state of a two-asset AMM pool and provides
    lightweight helper methods for querying reserves and token relationships.

    Attributes:
        token_x: Symbol of token X.
        token_y: Symbol of token Y.
        reserve_x: Reserve amount of token X.
        reserve_y: Reserve amount of token Y.
        fee_rate: Trading fee rate charged on the raw input amount.
    """

    token_x: str
    token_y: str
    reserve_x: float
    reserve_y: float
    fee_rate: float = 0.003

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate pool state and configuration."""
        if self.reserve_x <= 0 or self.reserve_y <= 0:
            raise InvalidReserveError(
                f"Pool reserves must be positive. Got reserve_x={self.reserve_x}, "
                f"reserve_y={self.reserve_y}."
            )

        if not (0.0 <= self.fee_rate < 1.0):
            raise InvalidReserveError(
                f"Fee rate must be in [0, 1). Got fee_rate={self.fee_rate}."
            )

        if self.token_x == self.token_y:
            raise InvalidReserveError("Pool tokens must be distinct.")

    @property
    def invariant(self) -> float:
        """Return the current constant-product invariant k = x * y."""
        return self.reserve_x * self.reserve_y

    def contains_token(self, token: str) -> bool:
        """Return whether the token belongs to the pool."""
        return token in {self.token_x, self.token_y}

    def get_reserve(self, token: str) -> float:
        """Return reserve for a given token symbol."""
        if token == self.token_x:
            return self.reserve_x
        if token == self.token_y:
            return self.reserve_y
        raise KeyError(f"Token {token} not found in pool.")

    def get_other_token(self, token: str) -> str:
        """Return the other token in the pool."""
        if token == self.token_x:
            return self.token_y
        if token == self.token_y:
            return self.token_x
        raise KeyError(f"Token {token} not found in pool.")

    def reserves(self) -> dict[str, float]:
        """Return pool reserves as a token-to-reserve mapping."""
        return {
            self.token_x: self.reserve_x,
            self.token_y: self.reserve_y,
        }

    def trade_size_ratio(self, token_in: str, amount_in: float) -> float:
        """Measure trade size relative to the input-side reserve.

        This is useful for research and diagnostics because execution quality
        depends strongly on the fraction of pool liquidity consumed.

        Args:
            token_in: Input token symbol.
            amount_in: Raw trade size.

        Returns:
            amount_in / reserve_in
        """
        reserve_in = self.get_reserve(token_in)
        return amount_in / reserve_in

    def copy(self) -> "AMMPool":
        """Return a copy of the pool state."""
        return AMMPool(
            token_x=self.token_x,
            token_y=self.token_y,
            reserve_x=self.reserve_x,
            reserve_y=self.reserve_y,
            fee_rate=self.fee_rate,
        )