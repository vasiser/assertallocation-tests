"""Data-driven functional cases TC-02 .. TC-14.

Each pytest.param id matches a case in docs/manual_test_cases.md, where the
test data and expected-value arithmetic are spelled out.
"""
import allure
import pytest

from rebalancer import rebalance
from conftest import make_account

HAPPY = [allure.feature("Happy path"), allure.severity(allure.severity_level.CRITICAL)]
BOUNDARY = [allure.feature("Boundary & rounding"), allure.severity(allure.severity_level.CRITICAL)]
BOUNDARY_NORMAL = [allure.feature("Boundary & rounding"), allure.severity(allure.severity_level.NORMAL)]
EDGE = [allure.feature("Boundary & rounding"), allure.severity(allure.severity_level.MINOR)]

CASES = [
    pytest.param(
        [("A", 25, 25, 100), ("B", 25, 25, 50), ("C", 25, 25, 200), ("D", 25, 25, 10)],
        "100000",
        [("A", "HOLD", 0), ("B", "HOLD", 0), ("C", "HOLD", 0), ("D", "HOLD", 0)],
        id="TC-02-all-at-target",
        marks=HAPPY,
    ),
    pytest.param(
        [("A", 20, 10, 100), ("B", 20, 30, 250), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)],
        "100000",
        [("A", "BUY", 100), ("B", "SELL", 40), ("C", "HOLD", 0), ("D", "HOLD", 0), ("E", "HOLD", 0)],
        id="TC-03-exact-division",
        marks=HAPPY,
    ),
    pytest.param(
        [("A", 30, 10, 70), ("B", 30, 20, 90), ("C", 20, 40, 300), ("D", 20, 30, 45)],
        "100000",
        [("A", "BUY", 285), ("B", "BUY", 111), ("C", "SELL", 66), ("D", "SELL", 222)],
        id="TC-04-multiple-buys-and-sells",
        marks=HAPPY,
    ),
    pytest.param(
        [("A", "20.1", 20, 450), ("B", "19.9", 20, 450), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)],
        "100000",
        [("A", "HOLD", 0), ("B", "HOLD", 0), ("C", "HOLD", 0), ("D", "HOLD", 0), ("E", "HOLD", 0)],
        id="TC-05-sub-share-variance",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("A", "20.45", 20, 450), ("B", "19.55", 20, 450), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)],
        "100000",
        [("A", "BUY", 1), ("B", "SELL", 1), ("C", "HOLD", 0), ("D", "HOLD", 0), ("E", "HOLD", 0)],
        id="TC-06-exactly-one-share",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("A", 19, 20, 90), ("B", 21, 20, 90), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)],
        "89999",
        [("A", "SELL", 9), ("B", "BUY", 9), ("C", "HOLD", 0), ("D", "HOLD", 0), ("E", "HOLD", 0)],
        id="TC-07-one-cent-short-of-next-share",
        marks=BOUNDARY,
    ),
    pytest.param(
        # 1% of $30 = $0.30 at $0.10/share = exactly 3 shares. Binary floats
        # compute 0.3 / 0.1 = 2.9999999999999996, which would truncate to 2.
        [("A", 19, 20, "0.10"), ("B", 21, 20, "0.10"), ("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)],
        "30",
        [("A", "SELL", 3), ("B", "BUY", 3), ("C", "HOLD", 0), ("D", "HOLD", 0), ("E", "HOLD", 0)],
        id="TC-08-penny-precision-price",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("A", 0, 25, 40), ("B", 40, 15, 300), ("C", 30, 30, 50), ("D", 30, 30, 60)],
        "100000",
        [("A", "SELL", 625), ("B", "BUY", 83), ("C", "HOLD", 0), ("D", "HOLD", 0)],
        id="TC-09-zero-target-full-liquidation",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("A", 25, 0, 125), ("B", 25, 50, 500), ("C", 25, 25, 50), ("D", 25, 25, 60)],
        "100000",
        [("A", "BUY", 200), ("B", "SELL", 50), ("C", "HOLD", 0), ("D", "HOLD", 0)],
        id="TC-10-new-security-acquisition",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("A", 10, 20, 100), ("B", 30, 20, 60), ("C", 30, 30, 50), ("D", 30, 30, 40)],
        "50",
        [("A", "HOLD", 0), ("B", "HOLD", 0), ("C", "HOLD", 0), ("D", "HOLD", 0)],
        id="TC-11-tiny-total-assets",
        marks=BOUNDARY_NORMAL,
    ),
    pytest.param(
        [("A", 10, 20, 333), ("B", 30, 20, 77), ("C", 30, 30, 50), ("D", 30, 30, 60)],
        "10000000",
        [("A", "SELL", 3003), ("B", "BUY", 12987), ("C", "HOLD", 0), ("D", "HOLD", 0)],
        id="TC-12-large-account",
        marks=BOUNDARY,
    ),
    pytest.param(
        [("IBM", 20, 10, 150), ("MSFT", 20, 20, 90), ("ORCL", 20, 30, 220), ("AAPL", 20, 20, 450), ("HD", 20, 20, 70)],
        "0",
        [("IBM", "HOLD", 0), ("MSFT", "HOLD", 0), ("ORCL", "HOLD", 0), ("AAPL", "HOLD", 0), ("HD", "HOLD", 0)],
        id="TC-13-zero-total-assets",
        marks=EDGE,
    ),
    pytest.param(
        [("A", 100, 100, 150)],
        "100000",
        [("A", "HOLD", 0)],
        id="TC-14-single-security-at-target",
        marks=EDGE,
    ),
]


@pytest.mark.parametrize("holdings_spec, total_assets, expected", CASES)
def test_rebalance_case(holdings_spec, total_assets, expected, request):
    allure.dynamic.title(request.node.callspec.id)
    account = make_account(holdings_spec, total_assets=total_assets)
    trades = rebalance(account)
    assert [(t.symbol, t.action, t.shares) for t in trades] == expected
