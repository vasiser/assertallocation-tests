"""Demo entrypoint: rebalance the assessment's sample account ABC.

Run from the repo root:
    $env:PYTHONPATH = "src"; python -m rebalancer
"""
from decimal import Decimal

from rebalancer import Account, Holding, rebalance

SAMPLE_ROWS = [
    ("IBM", "20", "10", "150"),
    ("MSFT", "20", "20", "90"),
    ("ORCL", "20", "30", "220"),
    ("AAPL", "20", "20", "450"),
    ("HD", "20", "20", "70"),
]


def build_sample_account() -> Account:
    holdings = tuple(
        Holding(symbol, Decimal(target), Decimal(current), Decimal(price))
        for symbol, target, current, price in SAMPLE_ROWS
    )
    return Account(account_id="ABC", total_assets=Decimal("100000"), holdings=holdings)


def main() -> None:
    account = build_sample_account()
    print(f"Account {account.account_id} — total assets ${account.total_assets:,}")
    print()
    print(f"{'Security':<10}{'Target %':>10}{'Current %':>11}{'Price':>10}  {'Action':<6}{'Shares':>8}")
    for holding, trade in zip(account.holdings, rebalance(account)):
        print(
            f"{holding.symbol:<10}{holding.target_pct:>10}{holding.current_pct:>11}"
            f"{holding.unit_price:>10}  {trade.action:<6}{trade.shares:>8}"
        )


if __name__ == "__main__":
    main()
