from __future__ import annotations

from dataclasses import dataclass

from src.amm.pool import AMMPool
from src.amm.swap import SwapResult, execute_swap
from src.execution.gas import GasModel
from src.types.common import Side
from src.utils.exceptions import InvalidSwapInputError


@dataclass(frozen=True)
class ExecutionResult:
    """Execution outcome after swap plus gas cost accounting."""

    side: Side
    swap_result: SwapResult
    gas_cost_usdc: float
    net_cash_flow_usdc: float
    net_eth_flow: float
    execution_mode: str


class ExecutionEngine:
    """Executes trades against the AMM pool.

    Conventions:
    - BUY ETH uses USDC as input token.
    - SELL ETH uses ETH as input token.
    - gas is charged in USDC.

    This class supports two execution modes:
    - defi-aware: execute through AMM with slippage + fee + gas
    - frictionless: execute at external price with optional gas
    """

    def __init__(self, gas_model: GasModel) -> None:
        self.gas_model = gas_model

    def execute(self, pool: AMMPool, side: Side, size: float) -> ExecutionResult:
        """Execute a buy or sell instruction through the AMM."""
        if side == Side.HOLD:
            raise InvalidSwapInputError("ExecutionEngine cannot execute HOLD signals.")

        if size <= 0:
            raise InvalidSwapInputError(f"Trade size must be positive. Got size={size}.")

        gas_cost = self.gas_model.estimate_cost()

        if side == Side.BUY:
            swap_result = execute_swap(pool, token_in="USDC", amount_in=size)
            net_cash_flow_usdc = -(swap_result.amount_in + gas_cost)
            net_eth_flow = swap_result.amount_out
        elif side == Side.SELL:
            swap_result = execute_swap(pool, token_in="ETH", amount_in=size)
            net_cash_flow_usdc = swap_result.amount_out - gas_cost
            net_eth_flow = -swap_result.amount_in
        else:
            raise InvalidSwapInputError(f"Unsupported side: {side}")

        return ExecutionResult(
            side=side,
            swap_result=swap_result,
            gas_cost_usdc=gas_cost,
            net_cash_flow_usdc=net_cash_flow_usdc,
            net_eth_flow=net_eth_flow,
            execution_mode="defi-aware",
        )

    def execute_frictionless(
        self,
        side: Side,
        size: float,
        external_price: float,
        include_gas: bool = False,
    ) -> ExecutionResult:
        """Execute a trade at the external reference price.

        Args:
            side: BUY or SELL.
            size:
                - BUY: size is USDC notional spent.
                - SELL: size is ETH quantity sold.
            external_price: Reference price in USDC per ETH.
            include_gas: Whether to charge gas in this frictionless baseline.

        Returns:
            ExecutionResult with a synthetic swap_result=None-like placeholder.

        Notes:
            This is a research baseline used to quantify the effect of AMM
            execution frictions relative to idealized fills.
        """
        if side == Side.HOLD:
            raise InvalidSwapInputError("ExecutionEngine cannot execute HOLD signals.")

        if size <= 0:
            raise InvalidSwapInputError(f"Trade size must be positive. Got size={size}.")

        if external_price <= 0:
            raise InvalidSwapInputError(
                f"external_price must be positive. Got external_price={external_price}."
            )

        gas_cost = self.gas_model.estimate_cost() if include_gas else 0.0

        if side == Side.BUY:
            eth_bought = size / external_price
            net_cash_flow_usdc = -(size + gas_cost)
            net_eth_flow = eth_bought

            synthetic_swap = SwapResult(
                token_in="USDC",
                token_out="ETH",
                amount_in=size,
                amount_out=eth_bought,
                fee_paid=0.0,
                reserve_x_before=0.0,
                reserve_y_before=0.0,
                reserve_x_after=0.0,
                reserve_y_after=0.0,
                spot_price_before=external_price,
                spot_price_after=external_price,
                mid_price_before=external_price,
                execution_price=external_price,
                price_impact=0.0,
                trade_size_ratio=0.0,
            )
        elif side == Side.SELL:
            usdc_received = size * external_price
            net_cash_flow_usdc = usdc_received - gas_cost
            net_eth_flow = -size

            synthetic_swap = SwapResult(
                token_in="ETH",
                token_out="USDC",
                amount_in=size,
                amount_out=usdc_received,
                fee_paid=0.0,
                reserve_x_before=0.0,
                reserve_y_before=0.0,
                reserve_x_after=0.0,
                reserve_y_after=0.0,
                spot_price_before=external_price,
                spot_price_after=external_price,
                mid_price_before=1 / external_price,
                execution_price=external_price,
                price_impact=0.0,
                trade_size_ratio=0.0,
            )
        else:
            raise InvalidSwapInputError(f"Unsupported side: {side}")

        return ExecutionResult(
            side=side,
            swap_result=synthetic_swap,
            gas_cost_usdc=gas_cost,
            net_cash_flow_usdc=net_cash_flow_usdc,
            net_eth_flow=net_eth_flow,
            execution_mode="frictionless",
        )