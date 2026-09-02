from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from rebalancer.models import Account, TradeInstruction

_HUNDRED = Decimal("100")


def _validate(account: Account) -> None:
    if not account.holdings:
        raise ValueError("account must contain at least one holding")
    if account.total_assets < 0:
        raise ValueError("total assets cannot be negative")

    seen: set[str] = set()
    for holding in account.holdings:
        if holding.symbol in seen:
            raise ValueError(f"duplicate security symbol: {holding.symbol}")
        seen.add(holding.symbol)
        if holding.unit_price <= 0:
            raise ValueError(f"{holding.symbol}: unit price must be positive")
        if holding.target_pct < 0:
            raise ValueError(f"{holding.symbol}: target percentage cannot be negative")
        if holding.current_pct < 0:
            raise ValueError(f"{holding.symbol}: current percentage cannot be negative")

    target_sum = sum(h.target_pct for h in account.holdings)
    if target_sum != _HUNDRED:
        raise ValueError(f"target percentages must sum to 100, got {target_sum}")
    current_sum = sum(h.current_pct for h in account.holdings)
    if current_sum != _HUNDRED:
        raise ValueError(f"current percentages must sum to 100, got {current_sum}")


def rebalance(account: Account) -> list[TradeInstruction]:
    """Compute whole-share trades that move each holding toward its target.

    Shares are truncated toward zero (ROUND_DOWN) so a trade never overshoots
    the target allocation; a variance smaller than one share's value yields HOLD.
    """
    _validate(account)

    instructions: list[TradeInstruction] = []
    for holding in account.holdings:
        variance_pct = holding.current_pct - holding.target_pct
        trade_value = abs(variance_pct) / _HUNDRED * account.total_assets
        shares = int(
            (trade_value / holding.unit_price).to_integral_value(rounding=ROUND_DOWN)
        )
        if shares == 0:
            action = "HOLD"
        elif variance_pct < 0:
            action = "BUY"
        else:
            action = "SELL"
        instructions.append(TradeInstruction(holding.symbol, action, shares))
    return instructions
