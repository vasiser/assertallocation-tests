from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

Action = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class Holding:
    """One security line as provided by the upstream system.

    Percentages are expressed on a 0-100 scale (20 means 20%).
    """

    symbol: str
    target_pct: Decimal
    current_pct: Decimal
    unit_price: Decimal


@dataclass(frozen=True)
class Account:
    account_id: str
    total_assets: Decimal
    holdings: tuple[Holding, ...]


@dataclass(frozen=True)
class TradeInstruction:
    """Output row: shares is always >= 0, direction is carried by action."""

    symbol: str
    action: Action
    shares: int
