from __future__ import annotations

import csv
from pathlib import Path

from src.data.market_paths import get_market_paths
from src.amm.pool import AMMPool
from src.backtest.engine import BacktestEngine
from src.execution.engine import ExecutionEngine
from src.execution.gas import GasModel
from src.portfolio.portfolio import Portfolio
from src.strategies.arbitrage import SimpleArbitrageStrategy
from src.types.common import MarketSnapshot


# ---------- Core Runner ----------

def run_single_experiment(
    market_name: str,
    market_data: list[MarketSnapshot],
    buy_size: float,
    threshold: float,
    gas: float,
) -> dict:
    """Run one experiment under a given market regime and parameter setting."""

    # ---- DeFi-aware ----
    pool_defi = AMMPool("ETH", "USDC", 100.0, 200000.0, 0.003)
    portfolio_defi = Portfolio(10000.0)
    strategy_defi = SimpleArbitrageStrategy(
        buy_threshold_bps=threshold,
        sell_threshold_bps=threshold,
        buy_size_usdc=buy_size,
        sell_size_eth=0.4,
    )
    exec_engine_defi = ExecutionEngine(GasModel(gas))
    engine_defi = BacktestEngine(
        pool_defi,
        portfolio_defi,
        strategy_defi,
        exec_engine_defi,
        logger_name=f"ExpDeFi_{market_name}_size{buy_size}_thr{threshold}_gas{gas}",
    )

    engine_defi.run(market_data, execution_mode="defi-aware")
    final_defi = portfolio_defi.equity(market_data[-1].external_price)

    # ---- Frictionless ----
    pool_fric = AMMPool("ETH", "USDC", 100.0, 200000.0, 0.003)
    portfolio_fric = Portfolio(10000.0)
    strategy_fric = SimpleArbitrageStrategy(
        buy_threshold_bps=threshold,
        sell_threshold_bps=threshold,
        buy_size_usdc=buy_size,
        sell_size_eth=0.4,
    )
    exec_engine_fric = ExecutionEngine(GasModel(gas))
    engine_fric = BacktestEngine(
        pool_fric,
        portfolio_fric,
        strategy_fric,
        exec_engine_fric,
        logger_name=f"ExpFric_{market_name}_size{buy_size}_thr{threshold}_gas{gas}",
    )

    engine_fric.run(
        market_data,
        execution_mode="frictionless",
        frictionless_include_gas=False,
    )
    final_fric = portfolio_fric.equity(market_data[-1].external_price)

    return {
        "market_regime": market_name,
        "buy_size": buy_size,
        "threshold_bps": threshold,
        "gas": gas,
        "defi_final_equity": final_defi,
        "defi_pnl": final_defi - 10000.0,
        "fric_final_equity": final_fric,
        "fric_pnl": final_fric - 10000.0,
        "defi_trades": portfolio_defi.trade_count,
        "fric_trades": portfolio_fric.trade_count,
        "defi_gas_spent": portfolio_defi.gas_spent_usdc,
        "fric_gas_spent": portfolio_fric.gas_spent_usdc,
        "final_defi_eth_qty": portfolio_defi.eth_position.quantity,
        "final_fric_eth_qty": portfolio_fric.eth_position.quantity,
        "friction_gap": final_fric - final_defi,
    }


# ---------- Batch Runner ----------

def run_experiments() -> None:
    """Run parameter sweep across multiple market regimes."""

    market_paths = get_market_paths()

    buy_sizes = [500, 1000, 2000]
    thresholds = [20, 40, 80]
    gas_values = [0, 5, 10]

    results: list[dict] = []

    print("Starting Day 3 multi-market experiments...")

    for market_name, market_data in market_paths.items():
        for buy_size in buy_sizes:
            for threshold in thresholds:
                for gas in gas_values:
                    print(
                        f"Running: market={market_name}, "
                        f"size={buy_size}, thr={threshold}, gas={gas}"
                    )

                    res = run_single_experiment(
                        market_name=market_name,
                        market_data=market_data,
                        buy_size=buy_size,
                        threshold=threshold,
                        gas=gas,
                    )
                    results.append(res)

    output_path = Path("outputs/tables/day3_multi_market_experiments.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to: {output_path}")
    print(f"Total experiments: {len(results)}")


# ---------- Entry ----------

if __name__ == "__main__":
    run_experiments()