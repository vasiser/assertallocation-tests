# Portfolio Rebalancer — QA Technical Assessment

<!-- Replace <OWNER> with the GitHub account name once the repo is pushed -->
![CI](https://github.com/<OWNER>/assertallocation-tests/actions/workflows/ci.yml/badge.svg)

Manual and automated test cases for a portfolio **rebalancing application**, plus a small reference implementation used as the system under test.

## The problem

Account **ABC** holds $100,000 fully invested across five securities, each with a 20% target allocation:

| Security | Target % | Current % | Variance | Unit price | Expected output |
|----------|---------:|----------:|---------:|-----------:|-----------------|
| IBM      | 20 | 10 | −10 | $150 | **BUY 66** ($10,000 / 150 = 66.67 → 66) |
| MSFT     | 20 | 20 |   0 |  $90 | HOLD 0 |
| ORCL     | 20 | 30 | +10 | $220 | **SELL 45** ($10,000 / 220 = 45.45 → 45) |
| AAPL     | 20 | 20 |   0 | $450 | HOLD 0 |
| HD       | 20 | 20 |   0 |  $70 | HOLD 0 |

Negative variance means buy, positive means sell. Shares are whole numbers, truncated toward zero so a trade never overshoots its target — see [docs/assumptions.md](docs/assumptions.md) for every assumption and the open questions worth discussing.

## Answer: reaching zero target variance

To correct the variances, **buy 66 shares of IBM** (66 × $150 = $9,900) and **sell 45 shares of ORCL** (45 × $220 = $9,900). MSFT, AAPL, and HD are already at their 20% targets — no action.

With whole shares, *exactly* zero variance is unreachable: after trading, IBM remains $100 under target and ORCL $100 over (the fractional remainders of $10,000/150 = 66.67 and $10,000/220 = 45.45). The application reduces every variance to below one share's value — the closest achievable to zero without overshooting a target. Allowing fractional shares (buy 66.67, sell 45.45) would reach exactly zero; see the assumptions for why whole shares were chosen.

## Project layout

| Path | Purpose |
|------|---------|
| `src/rebalancer/` | Reference implementation (system under test): `models.py` dataclasses, `rebalance.py` calculation + input validation, `__main__.py` demo |
| `docs/manual_test_cases.md` | **Deliverable 1:** manual test case catalog — 21 cases (TC-01 … TC-20b) covering happy path, boundary/rounding, and validation |
| `docs/assumptions.md` | Explicit assumptions + open questions for discussion |
| `tests/` | **Deliverable 2:** automated pytest suite (35 tests) |

## Running

```powershell
pip install -r requirements.txt   # pytest + allure-pytest
python -m pytest -v               # run all 35 tests
```

Demo (prints the ABC account result table):

```powershell
$env:PYTHONPATH = "src"; python -m rebalancer
```

## Allure report

Test results can be exported in [Allure](https://allurereport.org/) format, where the suite appears grouped by the manual catalog's categories (Happy path / Boundary & rounding / Validation / Invariants) with severities and TC-ID titles:

```powershell
python -m pytest --alluredir=allure-results --clean-alluredir
allure serve allure-results       # generates the report and opens it in the browser
```

Viewing requires the Allure CLI (`scoop install allure`; needs Java, e.g. `scoop install temurin-lts-jdk` — or via Node: `npm install -g allure-commandline`). The CLI is only needed for *viewing*: generating `allure-results` works with just `allure-pytest` from requirements.txt.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs the full suite on Python 3.12 for every push and pull request to `main`; it can also be triggered manually via **Actions → CI → Run workflow**. Each run uploads its Allure results as an `allure-results` build artifact (kept 14 days) — download it from the run's page in the Actions tab, unzip, and view with `allure serve <folder>`. The artifact is uploaded even when tests fail, which is when the report matters most.

## Test design

- **`tests/test_rebalance_sample.py`** — the acceptance test: asserts the full instruction list for account ABC exactly, including output order.
- **`tests/test_rebalance_cases.py`** — data-driven functional cases via `pytest.mark.parametrize`. Each pytest ID (`TC-03-exact-division`, `TC-08-penny-precision-price`, …) maps 1:1 to a row in the manual catalog, giving full manual↔automated traceability.
- **`tests/test_validation.py`** — invalid inputs (percentages not summing to 100, non-positive prices, duplicates, empty account, negative values) are rejected with descriptive errors.
- **`tests/test_invariants.py`** — property-style rules checked across representative accounts: trades never overshoot the target, the residual is always smaller than one share's value, and actions always match the variance sign. The sample account's cash neutrality ($9,900 bought = $9,900 sold) is asserted as a specific fact — floor-rounding does not guarantee it in general.

Money and percentages use Python `Decimal` throughout: 0.1 has no exact binary representation, and TC-08 demonstrates a case where float arithmetic would produce 99 shares instead of the correct 100.

**With more time:** property-based testing with [hypothesis](https://hypothesis.readthedocs.io/) — generate random valid accounts and check the invariants above hold universally; and an upstream adapter deriving current % from held share counts × prices.
