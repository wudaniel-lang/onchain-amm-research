from __future__ import annotations

from src.amm.pool import AMMPool
from src.amm.swap import execute_swap
from src.config.loader import load_config
from src.utils.logger import setup_logger


def build_default_pool() -> AMMPool:
    """Build the default AMM pool from config.

    Returns:
        AMMPool initialized from configs/base.yaml.
    """
    config = load_config()

    return AMMPool(
        token_x=config.amm.default_token_x,
        token_y=config.amm.default_token_y,
        reserve_x=config.amm.default_reserve_x,
        reserve_y=config.amm.default_reserve_y,
        fee_rate=config.amm.default_fee_rate,
    )


def run_day1_demo() -> None:
    """Run a minimal Day 1 AMM demo.

    This function demonstrates:
    - config loading
    - logger initialization
    - pool initialization
    - swap execution
    - research-oriented metric reporting
    """
    config = load_config()
    logger = setup_logger(__name__, config.logging)

    pool = build_default_pool()

    logger.info("Project: %s", config.project.name)
    logger.info("Environment: %s", config.project.environment)
    logger.info(
        "Initialized AMM pool: %s/%s | reserve_x=%.4f | reserve_y=%.4f | fee_rate=%.4f",
        pool.token_x,
        pool.token_y,
        pool.reserve_x,
        pool.reserve_y,
        pool.fee_rate,
    )

    trade_amount = 1000.0
    result = execute_swap(pool, token_in=pool.token_y, amount_in=trade_amount)

    logger.info("Executed sample swap: %.4f %s -> %.6f %s", result.amount_in, result.token_in, result.amount_out, result.token_out)
    logger.info("Fee paid: %.6f %s", result.fee_paid, result.token_in)
    logger.info("Mid price before: %.6f", result.mid_price_before)
    logger.info("Execution price: %.6f", result.execution_price)
    logger.info("Price impact: %.6f", result.price_impact)
    logger.info("Trade size ratio: %.6f", result.trade_size_ratio)
    logger.info(
        "Post-trade reserves: %s=%.6f | %s=%.6f",
        pool.token_x,
        pool.reserve_x,
        pool.token_y,
        pool.reserve_y,
    )


if __name__ == "__main__":
    run_day1_demo()