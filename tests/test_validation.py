"""Validation cases TC-13 .. TC-20: invalid input is rejected with a clear error.

Each pytest.param id matches a case in docs/manual_test_cases.md.
"""
import pytest

from rebalancer import rebalance
from conftest import make_account

VALID_FILLER = [("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)]

CASES = [
    pytest.param(
        [("A", 25, 20, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "target percentages must sum to 100",
        id="TC-13-targets-sum-not-100",
    ),
    pytest.param(
        [("A", 20, 25, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "current percentages must sum to 100",
        id="TC-14-currents-sum-not-100",
    ),
    pytest.param(
        [("A", 20, 20, 0), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "unit price must be positive",
        id="TC-15-zero-unit-price",
    ),
    pytest.param(
        [("A", 20, 20, -90), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "unit price must be positive",
        id="TC-16-negative-unit-price",
    ),
    pytest.param(
        [("A", 20, 20, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "-100",
        "total assets cannot be negative",
        id="TC-17-negative-total-assets",
    ),
    pytest.param(
        [("A", 20, 20, 100), ("A", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "duplicate security symbol: A",
        id="TC-18-duplicate-symbol",
    ),
    pytest.param(
        [],
        "100000",
        "at least one holding",
        id="TC-19-empty-holdings",
    ),
    pytest.param(
        [("A", -20, 20, 100), ("B", 60, 20, 90)] + VALID_FILLER,
        "100000",
        "target percentage cannot be negative",
        id="TC-20-negative-target-pct",
    ),
    pytest.param(
        [("A", 20, -20, 100), ("B", 20, 60, 90)] + VALID_FILLER,
        "100000",
        "current percentage cannot be negative",
        id="TC-20b-negative-current-pct",
    ),
]


@pytest.mark.parametrize("holdings_spec, total_assets, error_match", CASES)
def test_invalid_input_rejected(holdings_spec, total_assets, error_match):
    account = make_account(holdings_spec, total_assets=total_assets)
    with pytest.raises(ValueError, match=error_match):
        rebalance(account)
