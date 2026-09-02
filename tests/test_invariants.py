"""Property-style invariants checked across a set of representative accounts.

These express what must hold for ANY valid rebalance, independent of the
specific expected numbers asserted in the case tests:

1. Never overshoot: the traded value (shares x price) never exceeds the
   absolute variance value the trade is correcting.
2. As close as whole shares allow: the residual after trading is strictly
   less than one unit price (otherwise one more share should have traded).
3. The action always matches the sign of the variance; HOLD means 0 shares;
   shares are never negative.
"""
from decimal import Decimal

import allure
import pytest

from rebalancer import rebalance
from conftest import SAMPLE_ROWS, make_account

pytestmark = [
    allure.feature("Invariants (automation-only)"),
    allure.severity(allure.severity_level.CRITICAL),
]

ACCOUNTS = [
    pytest.param(make_account(SAMPLE_ROWS, "100000", "ABC"), id="sample-abc"),
    pytest.param(
        make_account([("A", 30, 10, 70), ("B", 30, 20, 90), ("C", 20, 40, 300), ("D", 20, 30, 45)], "100000"),
        id="multi-buy-sell",
    ),
    pytest.param(
        make_account([("A", 0, 25, 40), ("B", 40, 15, 300), ("C", 30, 30, 50), ("D", 30, 30, 60)], "100000"),
        id="liquidation-and-buy",
    ),
    pytest.param(
        make_account([("A", 10, 20, 333), ("B", 30, 20, 77), ("C", 30, 30, 50), ("D", 30, 30, 60)], "10000000"),
        id="large-account",
    ),
    pytest.param(
        make_account([("A", "20.1", 20, 450), ("B", "19.9", 20, 450), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)], "100000"),
        id="sub-share-variances",
    ),
]


@pytest.mark.parametrize("account", ACCOUNTS)
def test_trades_never_overshoot_and_land_within_one_share(account, request):
    allure.dynamic.title(f"Never overshoot, land within one share: {request.node.callspec.id}")
    for holding, trade in zip(account.holdings, rebalance(account)):
        variance_value = (
            abs(holding.current_pct - holding.target_pct) / 100 * account.total_assets
        )
        traded_value = trade.shares * holding.unit_price
        assert traded_value <= variance_value, f"{trade.symbol} overshoots its target"
        assert variance_value - traded_value < holding.unit_price, (
            f"{trade.symbol} left more than one share's value untraded"
        )


@pytest.mark.parametrize("account", ACCOUNTS)
def test_action_matches_variance_sign(account, request):
    allure.dynamic.title(f"Action matches variance sign: {request.node.callspec.id}")
    for holding, trade in zip(account.holdings, rebalance(account)):
        variance = holding.current_pct - holding.target_pct
        assert trade.shares >= 0
        if trade.action == "BUY":
            assert variance < 0 and trade.shares > 0
        elif trade.action == "SELL":
            assert variance > 0 and trade.shares > 0
        else:
            assert trade.action == "HOLD" and trade.shares == 0


@allure.title("Sample account ABC is cash neutral ($9,900 bought = $9,900 sold)")
@allure.severity(allure.severity_level.NORMAL)
def test_sample_account_is_cash_neutral(sample_account):
    """Specific fact about account ABC, not a general invariant: buys and
    sells floor independently, but here both round to exactly $9,900."""
    trades = {t.symbol: t for t in rebalance(sample_account)}
    prices = {h.symbol: h.unit_price for h in sample_account.holdings}
    buy_cost = trades["IBM"].shares * prices["IBM"]
    sell_proceeds = trades["ORCL"].shares * prices["ORCL"]
    assert buy_cost == Decimal("9900")
    assert sell_proceeds == Decimal("9900")
