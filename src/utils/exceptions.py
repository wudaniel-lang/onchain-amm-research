class AMMError(Exception):
    """Base exception for AMM-related errors."""


class InvalidReserveError(AMMError):
    """Raised when reserves are non-positive or otherwise invalid."""


class InvalidSwapInputError(AMMError):
    """Raised when swap input parameters are invalid."""


class UnsupportedTokenError(AMMError):
    """Raised when attempting to trade a token not in the pool."""