from __future__ import annotations

from pathlib import Path

from src.amm.pool import AMMPool
from src.backtest.engine import BacktestEngine
from src.execution.engine import ExecutionEngine
from src.execution.gas import GasModel
from src.portfolio.portfolio import Portfolio
from src.strategies.arbitrage import SimpleArbitrageStrategy
from src.types.common import MarketSnapshot


def print_section(title: str) -> None:
    print()
    print("=" * 96)
    print(title)
    print("=" * 96)


def build_market_data() -> list[MarketSnapshot]:
    return [
        MarketSnapshot(timestamp="t1", external_price=2020.0),
        MarketSnapshot(timestamp="t2", external_price=2060.0),
        MarketSnapshot(timestamp="t3", external_price=2100.0),
        MarketSnapshot(timestamp="t4", external_price=1980.0),
        MarketSnapshot(timestamp="t5", external_price=1950.0),
        MarketSnapshot(timestamp="t6", external_price=2010.0),
        MarketSnapshot(timestamp="t7", external_price=2080.0),
    ]


def build_initial_pool() -> AMMPool:
    return AMMPool(
        token_x="ETH",
        token_y="USDC",
        reserve_x=100.0,
        reserve_y=200000.0,
        fee_rate=0.003,
    )


def build_strategy() -> SimpleArbitrageStrategy:
    return SimpleArbitrageStrategy(
        buy_threshold_bps=40.0,
        sell_threshold_bps=40.0,
        buy_size_usdc=1000.0,
        sell_size_eth=0.4,
    )


def run_defi_aware_demo(
    market_data: list[MarketSnapshot],
) -> tuple[BacktestEngine, object]:
    pool = build_initial_pool()
    portfolio = Portfolio(cash_usdc=10000.0)
    strategy = build_strategy()
    execution_engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))

    backtest_engine = BacktestEngine(
        pool=pool,
        portfolio=portfolio,
        strategy=strategy,
        execution_engine=execution_engine,
        logger_name="BacktestEngineDeFi",
    )
    result = backtest_engine.run(market_data, execution_mode="defi-aware")
    return backtest_engine, result


def run_frictionless_demo(
    market_data: list[MarketSnapshot],
) -> tuple[BacktestEngine, object]:
    # Important:
    # We still provide a real AMM pool for signal generation.
    # Only the execution model changes.
    pool = build_initial_pool()
    portfolio = Portfolio(cash_usdc=10000.0)
    strategy = build_strategy()
    execution_engine = ExecutionEngine(gas_model=GasModel(fixed_cost_usdc=5.0))

    backtest_engine = BacktestEngine(
        pool=pool,
        portfolio=portfolio,
        strategy=strategy,
        execution_engine=execution_engine,
        logger_name="BacktestEngineFrictionless",
    )
    result = backtest_engine.run(
        market_data,
        execution_mode="frictionless",
        frictionless_include_gas=False,
    )
    return backtest_engine, result


def print_result_summary(
    label: str,
    engine: BacktestEngine,
    result: object,
    last_price: float,
) -> None:
    portfolio = engine.portfolio
    final_equity = portfolio.equity(external_price=last_price)
    initial_equity = 10000.0

    print_section(label)
    print(f"Initial equity: {initial_equity:.4f} USDC")
    print(f"Final equity:   {final_equity:.4f} USDC")
    print(f"PnL:            {final_equity - initial_equity:.4f} USDC")
    print(f"Trades:         {portfolio.trade_count}")
    print(f"Gas spent:      {portfolio.gas_spent_usdc:.4f} USDC")
    print(f"Final cash:     {portfolio.cash_usdc:.4f} USDC")
    print(f"Final ETH qty:  {portfolio.eth_position.quantity:.6f}")
    print(f"Equity series:  {[round(x, 4) for x in result.equity_series()]}")

    for rec in result.records:
        print(
            f"{rec.timestamp} | mode={rec.execution_mode:>12} | "
            f"ext={rec.external_price:.2f} | amm_before={rec.amm_price_before:.2f} | "
            f"side={rec.side:>4} | size={rec.size:.4f} | "
            f"cash={rec.cash_usdc:.2f} | eth={rec.eth_qty:.6f} | equity={rec.equity_usdc:.2f}"
        )
        print(f"  reason: {rec.reason}")


def main() -> None:
    market_data = build_market_data()
    last_price = market_data[-1].external_price

    defi_engine, defi_result = run_defi_aware_demo(market_data)
    frictionless_engine, frictionless_result = run_frictionless_demo(market_data)

    output_dir = Path("outputs/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    defi_result.to_csv(output_dir / "day2_defi_aware_records.csv")
    frictionless_result.to_csv(output_dir / "day2_frictionless_records.csv")

    print_result_summary(
        "DAY 2 DEMO: DEFI-AWARE EXECUTION",
        defi_engine,
        defi_result,
        last_price,
    )
    print_result_summary(
        "DAY 2 DEMO: FRICTIONLESS BASELINE",
        frictionless_engine,
        frictionless_result,
        last_price,
    )

    print_section("A+ DAY 2 TAKEAWAYS")
    print("1. Both runs use the same signal logic and the same AMM reference state.")
    print("2. The only difference is how trades are executed.")
    print("3. This makes the frictionless run a valid counterfactual baseline.")
    print("4. The gap between the two runs measures execution friction more cleanly.")


if __name__ == "__main__":
    main()