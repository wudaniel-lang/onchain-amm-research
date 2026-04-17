from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def ensure_output_dir(path: Path) -> None:
    """Create output directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate that all required columns exist in the dataframe."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in CSV: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )


def add_bar_labels(ax: plt.Axes, fmt: str = "{:.1f}") -> None:
    """Annotate bars with numeric values."""
    for patch in ax.patches:
        height = patch.get_height()
        x = patch.get_x() + patch.get_width() / 2

        if height >= 0:
            y = height
            va = "bottom"
            offset = 2
        else:
            y = height
            va = "top"
            offset = -2

        ax.annotate(
            fmt.format(height),
            (x, y),
            textcoords="offset points",
            xytext=(0, offset),
            ha="center",
            va=va,
            fontsize=9,
        )


def apply_common_style(ax: plt.Axes, add_zero_line: bool = False) -> None:
    """Apply common plot styling."""
    ax.grid(True, linestyle="--", alpha=0.4)
    if add_zero_line:
        ax.axhline(0, linestyle="--", linewidth=1, alpha=0.8)


def main() -> None:
    # ---------- Paths ----------
    csv_path = Path("outputs/tables/day3_multi_market_experiments.csv")
    output_dir = Path("outputs/figures")
    ensure_output_dir(output_dir)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find experiment CSV at: {csv_path}\n"
            f"Please run scripts/experiments/run_experiment.py first."
        )

    # ---------- Load Data ----------
    df = pd.read_csv(csv_path)

    required_columns = [
        "market_regime",
        "buy_size",
        "threshold_bps",
        "gas",
        "defi_pnl",
        "fric_pnl",
        "friction_gap",
        "defi_trades",
        "final_defi_eth_qty",
        "final_fric_eth_qty",
    ]
    validate_columns(df, required_columns)

    print(f"Loaded data: {df.shape}")
    print("Columns:", list(df.columns))

    # Stable market order for consistent reporting
    preferred_order = ["trend_up", "trend_down", "reversal", "oscillation"]
    regimes_in_data = [r for r in preferred_order if r in df["market_regime"].unique()]
    if not regimes_in_data:
        regimes_in_data = sorted(df["market_regime"].unique())

    # =========================================================
    # Plot 1: Gas vs DeFi PnL (grouped by market regime)
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    for market in regimes_in_data:
        subset = df[df["market_regime"] == market]
        grouped = subset.groupby("gas", as_index=True)["defi_pnl"].mean().sort_index()
        ax.plot(grouped.index, grouped.values, marker="o", label=market)

    ax.set_xlabel("Gas Cost")
    ax.set_ylabel("Average DeFi PnL")
    ax.set_title("Gas Impact on DeFi Strategy Performance")
    ax.legend()
    apply_common_style(ax, add_zero_line=True)
    fig.tight_layout()
    fig.savefig(output_dir / "gas_vs_pnl.png")
    plt.close(fig)

    # =========================================================
    # Plot 2: Friction Gap by Market Regime
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    grouped_gap = (
        df.groupby("market_regime", as_index=True)["friction_gap"]
        .mean()
        .reindex(regimes_in_data)
    )

    ax.bar(grouped_gap.index, grouped_gap.values)
    ax.set_xlabel("Market Regime")
    ax.set_ylabel("Average Friction Gap (Frictionless - DeFi)")
    ax.set_title("Impact of Execution Frictions Across Market Regimes")
    apply_common_style(ax, add_zero_line=True)
    add_bar_labels(ax, fmt="{:.1f}")
    fig.tight_layout()
    fig.savefig(output_dir / "friction_gap.png")
    plt.close(fig)

    # =========================================================
    # Plot 3: Inventory Comparison by Execution Mode
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    grouped_defi_inv = (
        df.groupby("market_regime", as_index=True)["final_defi_eth_qty"]
        .mean()
        .reindex(regimes_in_data)
    )
    grouped_fric_inv = (
        df.groupby("market_regime", as_index=True)["final_fric_eth_qty"]
        .mean()
        .reindex(regimes_in_data)
    )

    x = list(range(len(regimes_in_data)))
    width = 0.38

    bars1 = ax.bar(
        [i - width / 2 for i in x],
        grouped_defi_inv.values,
        width=width,
        label="DeFi-aware",
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        grouped_fric_inv.values,
        width=width,
        label="Frictionless",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(regimes_in_data)
    ax.set_xlabel("Market Regime")
    ax.set_ylabel("Average Final ETH Position")
    ax.set_title("Inventory Accumulation by Execution Mode")
    ax.legend()
    apply_common_style(ax, add_zero_line=False)

    for bars in (bars1, bars2):
        for patch in bars:
            height = patch.get_height()
            ax.annotate(
                f"{height:.2f}",
                (patch.get_x() + patch.get_width() / 2, height),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    fig.tight_layout()
    fig.savefig(output_dir / "inventory.png")
    plt.close(fig)

    # =========================================================
    # Plot 4: Trade Size vs DeFi PnL (grouped by market regime)
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    for market in regimes_in_data:
        subset = df[df["market_regime"] == market]
        grouped = (
            subset.groupby("buy_size", as_index=True)["defi_pnl"].mean().sort_index()
        )
        ax.plot(grouped.index, grouped.values, marker="o", label=market)

    ax.set_xlabel("Trade Size (buy_size)")
    ax.set_ylabel("Average DeFi PnL")
    ax.set_title("Impact of Trade Size on Strategy Performance")
    ax.legend()
    apply_common_style(ax, add_zero_line=True)
    fig.tight_layout()
    fig.savefig(output_dir / "size_vs_pnl.png")
    plt.close(fig)

    # =========================================================
    # Plot 5: Trade Count by Market Regime
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    grouped_trades = (
        df.groupby("market_regime", as_index=True)["defi_trades"]
        .mean()
        .reindex(regimes_in_data)
    )

    ax.bar(grouped_trades.index, grouped_trades.values)
    ax.set_xlabel("Market Regime")
    ax.set_ylabel("Average Trade Count")
    ax.set_title("Trading Frequency Across Market Regimes")
    apply_common_style(ax, add_zero_line=False)
    add_bar_labels(ax, fmt="{:.2f}")
    fig.tight_layout()
    fig.savefig(output_dir / "trade_count.png")
    plt.close(fig)

    # =========================================================
    # Plot 6: Inventory vs PnL (scatter)
    # =========================================================
    fig, ax = plt.subplots(figsize=(8, 5))

    for market in regimes_in_data:
        subset = df[df["market_regime"] == market]
        ax.scatter(
            subset["final_defi_eth_qty"],
            subset["defi_pnl"],
            alpha=0.6,
            s=50,
            label=market,
        )

    ax.set_xlabel("Final DeFi ETH Position")
    ax.set_ylabel("DeFi PnL")
    ax.set_title("Relationship Between Inventory and Performance")
    ax.legend()
    apply_common_style(ax, add_zero_line=True)
    fig.tight_layout()
    fig.savefig(output_dir / "inventory_vs_pnl.png")
    plt.close(fig)

    print(f"All plots saved to: {output_dir.resolve()}")
    print("Generated files:")
    for filename in [
        "gas_vs_pnl.png",
        "friction_gap.png",
        "inventory.png",
        "size_vs_pnl.png",
        "trade_count.png",
        "inventory_vs_pnl.png",
    ]:
        print(f" - {output_dir / filename}")


if __name__ == "__main__":
    main()