from __future__ import annotations

from src.types.common import MarketSnapshot


def build_trend_up_path() -> list[MarketSnapshot]:
    """Monotonic upward trend."""
    prices = [2000.0, 2020.0, 2050.0, 2080.0, 2110.0, 2140.0, 2180.0]
    return [MarketSnapshot(timestamp=f"t{i+1}", external_price=p) for i, p in enumerate(prices)]


def build_trend_down_path() -> list[MarketSnapshot]:
    """Monotonic downward trend."""
    prices = [2100.0, 2070.0, 2040.0, 2000.0, 1970.0, 1940.0, 1900.0]
    return [MarketSnapshot(timestamp=f"t{i+1}", external_price=p) for i, p in enumerate(prices)]


def build_reversal_path() -> list[MarketSnapshot]:
    """Upward move followed by reversal and rebound."""
    prices = [2020.0, 2060.0, 2100.0, 1980.0, 1950.0, 2010.0, 2080.0]
    return [MarketSnapshot(timestamp=f"t{i+1}", external_price=p) for i, p in enumerate(prices)]


def build_oscillation_path() -> list[MarketSnapshot]:
    """Oscillating market around a rough anchor level."""
    prices = [2000.0, 2030.0, 1980.0, 2020.0, 1970.0, 2010.0, 1990.0]
    return [MarketSnapshot(timestamp=f"t{i+1}", external_price=p) for i, p in enumerate(prices)]


def get_market_paths() -> dict[str, list[MarketSnapshot]]:
    """Return all predefined market regimes."""
    return {
        "trend_up": build_trend_up_path(),
        "trend_down": build_trend_down_path(),
        "reversal": build_reversal_path(),
        "oscillation": build_oscillation_path(),
    }