"""TC-01: the exact assessment scenario (acceptance test).

Account ABC, $100K: IBM must be bought up from 10% to 20% ($10,000 at $150
buys 66 whole shares) and ORCL sold down from 30% to 20% ($10,000 at $220
sells 45 whole shares); the rest are already on target.
"""
from rebalancer import TradeInstruction, rebalance


def test_tc01_sample_account_abc(sample_account):
    assert rebalance(sample_account) == [
        TradeInstruction("IBM", "BUY", 66),
        TradeInstruction("MSFT", "HOLD", 0),
        TradeInstruction("ORCL", "SELL", 45),
        TradeInstruction("AAPL", "HOLD", 0),
        TradeInstruction("HD", "HOLD", 0),
    ]


def test_tc01_output_preserves_input_order(sample_account):
    symbols = [trade.symbol for trade in rebalance(sample_account)]
    assert symbols == ["IBM", "MSFT", "ORCL", "AAPL", "HD"]
