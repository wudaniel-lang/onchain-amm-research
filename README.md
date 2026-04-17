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

## Project Structure

```text
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