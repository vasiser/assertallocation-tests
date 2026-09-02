from decimal import Decimal

import pytest

from rebalancer import Account, Holding

SAMPLE_ROWS = [
    ("IBM", "20", "10", "150"),
    ("MSFT", "20", "20", "90"),
    ("ORCL", "20", "30", "220"),
    ("AAPL", "20", "20", "450"),
    ("HD", "20", "20", "70"),
]


def make_account(holdings_spec, total_assets="100000", account_id="TEST"):
    """Build an Account from compact (symbol, target_pct, current_pct, unit_price) tuples.

    Values may be str/int; they are converted to Decimal via str to avoid
    binary floating-point representation issues.
    """
    holdings = tuple(
        Holding(symbol, Decimal(str(target)), Decimal(str(current)), Decimal(str(price)))
        for symbol, target, current, price in holdings_spec
    )
    return Account(account_id, Decimal(str(total_assets)), holdings)


@pytest.fixture
def sample_account():
    """The assessment's account ABC: $100K, five securities, 20% target each."""
    return make_account(SAMPLE_ROWS, total_assets="100000", account_id="ABC")
