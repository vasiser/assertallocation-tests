"""Validation cases TC-15 .. TC-23: invalid input is rejected with a clear error.

Each pytest.param id matches a case in docs/manual_test_cases.md.
"""
import allure
import pytest

from rebalancer import rebalance
from conftest import make_account

pytestmark = [
    allure.feature("Validation"),
    allure.severity(allure.severity_level.NORMAL),
]

VALID_FILLER = [("C", 20, 20, 50), ("D", 20, 20, 60), ("E", 20, 20, 70)]

CASES = [
    pytest.param(
        [("A", 25, 20, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "target percentages must sum to 100",
        id="TC-15-targets-sum-not-100",
    ),
    pytest.param(
        [("A", 20, 25, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "current percentages must sum to 100",
        id="TC-16-currents-sum-not-100",
    ),
    pytest.param(
        [("A", 20, 20, 0), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "unit price must be positive",
        id="TC-17-zero-unit-price",
    ),
    pytest.param(
        [("A", 20, 20, -90), ("B", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "unit price must be positive",
        id="TC-18-negative-unit-price",
    ),
    pytest.param(
        [("A", 20, 20, 100), ("B", 20, 20, 90)] + VALID_FILLER,
        "-100",
        "total assets cannot be negative",
        id="TC-19-negative-total-assets",
    ),
    pytest.param(
        [("A", 20, 20, 100), ("A", 20, 20, 90)] + VALID_FILLER,
        "100000",
        "duplicate security symbol: A",
        id="TC-20-duplicate-symbol",
    ),
    pytest.param(
        [],
        "100000",
        "at least one holding",
        id="TC-21-empty-holdings",
    ),
    pytest.param(
        [("A", -20, 20, 100), ("B", 60, 20, 90)] + VALID_FILLER,
        "100000",
        "target percentage cannot be negative",
        id="TC-22-negative-target-pct",
    ),
    pytest.param(
        [("A", 20, -20, 100), ("B", 20, 60, 90)] + VALID_FILLER,
        "100000",
        "current percentage cannot be negative",
        id="TC-23-negative-current-pct",
    ),
]


@pytest.mark.parametrize("holdings_spec, total_assets, error_match", CASES)
def test_invalid_input_rejected(holdings_spec, total_assets, error_match, request):
    allure.dynamic.title(request.node.callspec.id)
    account = make_account(holdings_spec, total_assets=total_assets)
    with pytest.raises(ValueError, match=error_match):
        rebalance(account)
