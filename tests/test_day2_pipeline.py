from __future__ import annotations

from pathlib import Path

from src.amm.pool import AMMPool
from src.backtest.engine import BacktestEngine
from src.execution.engine import ExecutionEngine
from src.execution.gas import GasModel
from src.portfolio.portfolio import Portfolio
from src.strategies.arbitrage import SimpleArbitrageStrategy
from src.types.common import MarketSnapshot, Side


def build_strategy() -> SimpleArbitrageStrategy:
    return SimpleArbitrageStrategy(
        buy_threshold_bps=40.0,
        sell_threshold_bps=40.0,
        buy_size_usdc=1000.0,
        sell_size_eth=0.4,
    )


def build_market_data() -> list[MarketSnapshot]:
    return [
        MarketSnapshot(timestamp="t1", external_price=2050.0),
        MarketSnapshot(timestamp="t2", external_price=2100.0),
        MarketSnapshot(timestamp="t3", external_price=1980.0),
        MarketSnapshot(timestamp="t4", external_price=1950.0),
    ]


def test_day2_pipeline_runs_end_to_end_defi_aware() -> None:
    pool = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )
    portfolio = Portfolio(cash_usdc=10000.0)
    execution_engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))
    backtest_engine = BacktestEngine(
        pool=pool,
        portfolio=portfolio,
        strategy=build_strategy(),
        execution_engine=execution_engine,
    )

    result = backtest_engine.run(build_market_data(), execution_mode="defi-aware")

    assert len(result.records) == 4
    assert portfolio.trade_count >= 1
    assert portfolio.gas_spent_usdc >= 5.0
    assert result.final_equity() > 0.0
    assert len(result.equity_series()) == 4


def test_day2_pipeline_runs_end_to_end_frictionless() -> None:
    pool = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )
    portfolio = Portfolio(cash_usdc=10000.0)
    execution_engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))
    backtest_engine = BacktestEngine(
        pool=pool,
        portfolio=portfolio,
        strategy=build_strategy(),
        execution_engine=execution_engine,
    )

    result = backtest_engine.run(build_market_data(), execution_mode="frictionless")

    assert len(result.records) == 4
    assert result.final_equity() > 0.0
    assert portfolio.trade_count >= 1


def test_execute_frictionless_buy_and_sell() -> None:
    engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))

    buy_result = engine.execute_frictionless(
        side=Side.BUY,
        size=1000.0,
        external_price=2000.0,
        include_gas=False,
    )
    sell_result = engine.execute_frictionless(
        side=Side.SELL,
        size=0.5,
        external_price=2000.0,
        include_gas=False,
    )

    assert buy_result.net_cash_flow_usdc == -1000.0
    assert buy_result.net_eth_flow == 0.5
    assert sell_result.net_cash_flow_usdc == 1000.0
    assert sell_result.net_eth_flow == -0.5


def test_backtest_result_can_export_csv(tmp_path: Path) -> None:
    pool = AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )
    portfolio = Portfolio(cash_usdc=10000.0)
    execution_engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))
    backtest_engine = BacktestEngine(
        pool=pool,
        portfolio=portfolio,
        strategy=build_strategy(),
        execution_engine=execution_engine,
    )

    result = backtest_engine.run(build_market_data(), execution_mode="defi-aware")
    output_path = tmp_path / "records.csv"
    result.to_csv(output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("timestamp,external_price")