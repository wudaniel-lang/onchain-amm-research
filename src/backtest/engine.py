from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from src.amm.pool import AMMPool
from src.amm.pricing import spot_price
from src.execution.engine import ExecutionEngine, ExecutionResult
from src.portfolio.portfolio import Portfolio
from src.strategies.base import BaseStrategy
from src.types.common import MarketSnapshot, Side
from src.utils.logger import setup_logger


@dataclass
class BacktestRecord:
    """Single-step backtest record."""

    timestamp: str
    external_price: float
    amm_price_before: float
    side: str
    size: float
    execution_mode: str
    cash_usdc: float
    eth_qty: float
    equity_usdc: float
    gas_spent_usdc: float
    reason: str


@dataclass
class BacktestResult:
    """Container for backtest outputs."""

    records: list[BacktestRecord] = field(default_factory=list)
    executions: list[ExecutionResult] = field(default_factory=list)

    def final_equity(self) -> float:
        """Return final equity if records exist, else 0."""
        if not self.records:
            return 0.0
        return self.records[-1].equity_usdc

    def equity_series(self) -> list[float]:
        """Return time-ordered equity values."""
        return [record.equity_usdc for record in self.records]

    def to_csv(self, path: str | Path) -> None:
        """Export backtest records to CSV."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "timestamp",
                    "external_price",
                    "amm_price_before",
                    "side",
                    "size",
                    "execution_mode",
                    "cash_usdc",
                    "eth_qty",
                    "equity_usdc",
                    "gas_spent_usdc",
                    "reason",
                ]
            )
            for record in self.records:
                writer.writerow(
                    [
                        record.timestamp,
                        record.external_price,
                        record.amm_price_before,
                        record.side,
                        record.size,
                        record.execution_mode,
                        record.cash_usdc,
                        record.eth_qty,
                        record.equity_usdc,
                        record.gas_spent_usdc,
                        record.reason,
                    ]
                )


class BacktestEngine:
    """Event-style minimal backtest engine for Day 2.

    Design:
    - signal generation should be identical across execution modes
    - only execution differs between 'defi-aware' and 'frictionless'

    Therefore:
    - strategy always sees a signal_pool
    - in DeFi-aware mode, signal_pool is also mutated by execution
    - in frictionless mode, signal_pool is read-only reference state
    """

    def __init__(
        self,
        pool: AMMPool,
        portfolio: Portfolio,
        strategy: BaseStrategy,
        execution_engine: ExecutionEngine,
        logger_name: str = "BacktestEngine",
    ) -> None:
        self.pool = pool
        self.portfolio = portfolio
        self.strategy = strategy
        self.execution_engine = execution_engine

        class _LoggingConfig:
            level = "INFO"
            log_to_file = False
            log_dir = "outputs/logs"
            log_filename = "backtest.log"

        self.logger = setup_logger(logger_name, _LoggingConfig())

    def run(
        self,
        market_data: list[MarketSnapshot],
        execution_mode: str = "defi-aware",
        frictionless_include_gas: bool = False,
    ) -> BacktestResult:
        """Run the backtest over a sequence of market snapshots.

        Args:
            market_data: Ordered sequence of market snapshots.
            execution_mode:
                - 'defi-aware': signal from real AMM, execute on AMM
                - 'frictionless': signal from same AMM state, execute at external price
            frictionless_include_gas: whether to include gas in frictionless baseline

        Returns:
            BacktestResult containing per-step records and executions.
        """
        if execution_mode not in {"defi-aware", "frictionless"}:
            raise ValueError(f"Unsupported execution_mode: {execution_mode}")

        result = BacktestResult()

        # This pool is always used for signal generation.
        # In defi-aware mode it is also the execution pool and mutates over time.
        # In frictionless mode it remains unchanged, which cleanly isolates
        # the effect of execution assumptions.
        signal_pool = self.pool

        for market in market_data:
            amm_price_before = spot_price(
                signal_pool, base_token="ETH", quote_token="USDC"
            )

            signal = self.strategy.generate_signal(
                market=market,
                pool=signal_pool,
                portfolio=self.portfolio,
            )

            if signal.side != Side.HOLD:
                if execution_mode == "defi-aware":
                    execution = self.execution_engine.execute(
                        pool=signal_pool,
                        side=signal.side,
                        size=signal.size,
                    )
                else:  # frictionless
                    execution = self.execution_engine.execute_frictionless(
                        side=signal.side,
                        size=signal.size,
                        external_price=market.external_price,
                        include_gas=frictionless_include_gas,
                    )

                self.portfolio.apply_execution(execution)
                result.executions.append(execution)

                self.logger.info(
                    "%s | mode=%s | side=%s | size=%.4f | ext=%.2f | amm_before=%.2f | gas=%.2f",
                    market.timestamp,
                    execution_mode,
                    signal.side.value,
                    signal.size,
                    market.external_price,
                    amm_price_before,
                    execution.gas_cost_usdc,
                )
            else:
                self.logger.info(
                    "%s | mode=%s | side=hold | ext=%.2f | amm_before=%.2f",
                    market.timestamp,
                    execution_mode,
                    market.external_price,
                    amm_price_before,
                )

            snapshot = self.portfolio.snapshot(external_price=market.external_price)

            result.records.append(
                BacktestRecord(
                    timestamp=market.timestamp,
                    external_price=market.external_price,
                    amm_price_before=amm_price_before,
                    side=signal.side.value,
                    size=signal.size,
                    execution_mode=execution_mode,
                    cash_usdc=snapshot["cash_usdc"],
                    eth_qty=snapshot["eth_qty"],
                    equity_usdc=snapshot["equity_usdc"],
                    gas_spent_usdc=snapshot["gas_spent_usdc"],
                    reason=signal.reason,
                )
            )

        return result