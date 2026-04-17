# On-Chain AMM Backtesting Engine

## Overview

This project implements an **execution-aware backtesting engine** for decentralized exchanges (DEXs), with a focus on **Automated Market Makers (AMMs)**.

Traditional backtesting systems assume frictionless execution and are designed for order book-based markets. In contrast, this project explicitly models:

- AMM pricing mechanisms (constant product)
- Slippage and liquidity constraints
- Transaction costs (fees and gas)
- Execution feedback (trades affect future prices)

The system enables controlled experiments to study how execution frictions impact strategy performance across different market conditions.

---

## Key Contributions

This project goes beyond standard backtesting frameworks by:

1. **AMM-based Execution Modeling**
   - Implements constant product pricing
   - Models slippage and price impact

2. **Execution-Aware Simulation**
   - Trades update pool reserves
   - Future signals depend on past execution

3. **Dual Execution Modes**
   - DeFi-aware execution (realistic)
   - Frictionless execution (baseline)

4. **Multi-Market Evaluation**
   - Trend up / trend down / reversal / oscillation
   - Tests robustness across regimes

5. **Systematic Experimentation**
   - Parameter sweeps (gas, trade size, thresholds)
   - Aggregate evaluation metrics

---

## System Pipeline

```text
Market Data / Synthetic Paths
            ↓
       Strategy Signal
            ↓
   Execution Engine (AMM / Frictionless)
            ↓
        Portfolio Update
            ↓
      Backtest Engine Loop
            ↓
        Result Logging
            ↓
     Analysis & Visualization
Project Structure
project_root/
├── src/
│   ├── amm/               # AMM pricing and pool logic
│   ├── backtest/          # Backtest engine
│   ├── execution/         # Execution and gas modeling
│   ├── portfolio/         # Portfolio tracking
│   ├── strategies/        # Strategy implementations
│   ├── data/              # Market path generation
│   └── types/             # Shared data structures
│
├── scripts/
│   ├── experiments/
│   │   └── run_experiment.py
│   └── analysis/
│       └── plot_results.py
│
├── outputs/
│   ├── tables/            # CSV experiment results
│   └── figures/           # Generated plots
│
├── tests/                 # Unit tests
└── README.md
Installation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
How to Run
Step 1: Run Experiments
python scripts/experiments/run_experiment.py

This will:

Run parameter sweeps across:
Trade size
Threshold
Gas cost
Evaluate across multiple market regimes:
trend_up
trend_down
reversal
oscillation

Output:

outputs/tables/day3_multi_market_experiments.csv
Step 2: Generate Plots
python scripts/analysis/plot_results.py

Output:

outputs/figures/
├── gas_vs_pnl.png
├── friction_gap.png
├── inventory.png
├── size_vs_pnl.png
├── trade_count.png
└── inventory_vs_pnl.png
Strategy

The system implements a dislocation-based trading strategy:

Observes price difference between:
External market price
AMM price
Executes trades when deviation exceeds a threshold

Key parameters:

buy_size
threshold_bps
gas
Market Regimes

Synthetic price paths are used to simulate different market conditions:

Regime	Description
trend_up	Monotonic upward trend
trend_down	Monotonic downward trend
reversal	Trend reversal and rebound
oscillation	Sideways oscillating market
Evaluation Metrics

The system tracks:

Final equity (PnL)
Trade count
Gas cost
Inventory (ETH position)
Key Findings
1. Gas Costs Matter
Higher gas reduces profitability
Strongest impact in high-frequency environments
2. Execution Frictions Are Not Always Bad
Frictionless execution can underperform
Especially in reversal and oscillating markets
3. Market Regime Matters
Strategy performance varies significantly across regimes
No single parameter works universally
4. Inventory Risk Is Critical
Frictionless execution accumulates larger positions
Leads to higher exposure and volatility
MEV (Future Work)

This project focuses on:

Slippage
Gas costs
Execution feedback

An important extension is Miner Extractable Value (MEV), which involves:

Transaction ordering
Adversarial agents

Modeling MEV would require simulating mempool dynamics and is left for future work.

Testing

Run unit tests:

pytest -q
Summary

Execution is not just a cost — it fundamentally changes strategy behavior.

By integrating AMM mechanics and execution modeling, this system provides a more realistic and insightful framework for evaluating DeFi trading strategies.