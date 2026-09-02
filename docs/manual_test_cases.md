# Manual Test Cases — Portfolio Rebalancer

**Application under test:** the rebalancing calculator. Input: an account (total assets + per-security target %, current %, unit price). Output: one instruction per security — action (BUY / SELL / HOLD) and a whole number of shares.

**Key assumptions applied throughout** (see `assumptions.md` for the full list):
- Whole shares only; share counts are truncated toward zero so a trade never overshoots the target allocation.
- A non-zero variance too small to fund one whole share results in HOLD 0.
- Both target % and current % must each sum to exactly 100 ("100% is vested" = fully invested).

**Common steps for every functional case (TC-01 … TC-12, TC-17b):**
1. Create an account with the test data below.
2. Run the rebalance calculation.
3. Verify one instruction is returned per security, in input order, with the expected action and share count.

**Common steps for every validation case (TC-13 … TC-20):**
1. Attempt to run the rebalance calculation with the invalid test data below.
2. Verify the input is rejected with a clear, descriptive error naming the failed rule.

| ID | Title | Category | Preconditions | Test Data | Expected Result | Automated |
|----|-------|----------|---------------|-----------|-----------------|-----------|
| TC-01 | Sample account ABC (assessment scenario) | Happy path | Account with $100,000, fully vested | IBM 20/10 @150 · MSFT 20/20 @90 · ORCL 20/30 @220 · AAPL 20/20 @450 · HD 20/20 @70 | IBM **BUY 66** ($10,000/150 = 66.67 → 66) · MSFT HOLD 0 · ORCL **SELL 45** ($10,000/220 = 45.45 → 45) · AAPL HOLD 0 · HD HOLD 0 | ✔ `TC-01` |
| TC-02 | All holdings already at target | Happy path | $100,000; every variance is 0 | 4 securities, each target 25 / current 25 | All HOLD 0 — no trades generated | ✔ `TC-02` |
| TC-03 | Trade value divides evenly by price | Happy path | $100,000 | A 20/10 @100 · B 20/30 @250 · C, D, E 20/20 | A **BUY 100** ($10,000/100 exact) · B **SELL 40** ($10,000/250 exact) · C, D, E HOLD 0 — no rounding artifacts | ✔ `TC-03` |
| TC-04 | Multiple buys and multiple sells together | Happy path | $100,000 | A 30/10 @70 · B 30/20 @90 · C 20/40 @300 · D 20/30 @45 | A **BUY 285** (20,000/70 → 285.71) · B **BUY 111** (10,000/90 → 111.11) · C **SELL 66** (20,000/300 → 66.67) · D **SELL 222** (10,000/45 → 222.22) | ✔ `TC-04` |
| TC-05 | Variance smaller than one unit price | Boundary/rounding | $100,000; trade value $100 < price $450 | A 20.1/20 @450 · B 19.9/20 @450 · C, D, E 20/20 | A HOLD 0 and B HOLD 0 despite non-zero variance — cannot fund/deliver a whole share; C–E HOLD 0 | ✔ `TC-05` |
| TC-06 | Trade value exactly one unit price | Boundary/rounding | $100,000; trade value $450 = price $450 | A 20.45/20 @450 · B 19.55/20 @450 · C, D, E 20/20 | A **BUY 1** · B **SELL 1** — the minimum tradable boundary | ✔ `TC-06` |
| TC-07 | Trade value one cent short of the next share | Boundary/rounding | $89,999 total; 1% variance = $899.99, price $90 | A 19/20 @90 · B 21/20 @90 · C, D, E 20/20 | A **SELL 9** and B **BUY 9** ($899.99/90 = 9.99988… → 9, never 10) — round toward zero, no overshoot | ✔ `TC-07` |
| TC-08 | Penny-precision price (decimal arithmetic) | Boundary/rounding | $1,000 total; price $0.10; trade value $10.00 | A 19/20 @0.10 · B 21/20 @0.10 · C, D, E 20/20 | A **SELL 100** and B **BUY 100** — exactly 100, not 99 (binary floating point computes 10/0.1 = 99.999…; the app must use exact decimal arithmetic) | ✔ `TC-08` |
| TC-09 | Target 0% — full liquidation | Boundary/rounding | $100,000; one security must be exited | A 0/25 @40 · B 40/15 @300 · C 30/30 · D 30/30 | A **SELL 625** ($25,000/40 exact — position fully exited) · B **BUY 83** ($25,000/300 → 83.33) · C, D HOLD 0 | ✔ `TC-09` |
| TC-10 | New security — current 0%, target > 0% | Boundary/rounding | $100,000; one security not yet held | A 25/0 @125 · B 25/50 @500 · C 25/25 · D 25/25 | A **BUY 200** ($25,000/125 exact — new position opened) · B **SELL 50** · C, D HOLD 0 | ✔ `TC-10` |
| TC-11 | Total assets smaller than any unit price | Boundary/rounding | $50 total; all prices > any trade value | A 10/20 @100 · B 30/20 @60 · C 30/30 · D 30/30 | All HOLD 0 — every variance value ($5) is below one share's price | ✔ `TC-11` |
| TC-12 | Large account — no precision loss | Boundary/rounding | $10,000,000 total | A 10/20 @333 · B 30/20 @77 · C 30/30 · D 30/30 | A **SELL 3003** ($1,000,000/333 → 3003.003) · B **BUY 12987** ($1,000,000/77 → 12,987.01) · C, D HOLD 0 | ✔ `TC-12` |
| TC-21 | Single security at 100% target | Boundary/rounding | Account holds exactly one security | A 100/100 @150, total $100,000 | One instruction: A HOLD 0 — a fully concentrated, on-target account needs no trades | ✔ `TC-21` |
| TC-17b | Zero total assets | Boundary/rounding | Account exists with $0 | Total assets $0; IBM 20/10 @150 · MSFT 20/20 @90 · ORCL 20/30 @220 · AAPL 20/20 @450 · HD 20/20 @70 | Accepted (documented behavior): every trade value is $0 → all HOLD 0 | ✔ `TC-17b` |
| TC-13 | Target percentages do not sum to 100 | Validation | — | 5 securities with targets 20/20/20/20/25 (sum 105), valid currents | Rejected: error states target percentages must sum to 100 | ✔ `TC-13` |
| TC-14 | Current percentages do not sum to 100 | Validation | — | Valid targets (5 × 20); currents 10/20/30/20/25 (sum 105) | Rejected: error states current percentages must sum to 100 (fully-vested assumption) | ✔ `TC-14` |
| TC-15 | Zero unit price | Validation | — | Sample account, but MSFT price = 0 | Rejected: error states unit price must be positive (division by zero guarded) | ✔ `TC-15` |
| TC-16 | Negative unit price | Validation | — | Sample account, but MSFT price = −90 | Rejected: error states unit price must be positive | ✔ `TC-16` |
| TC-17 | Negative total assets | Validation | — | Sample account holdings, total assets = −$100 | Rejected: error states total assets cannot be negative | ✔ `TC-17` |
| TC-18 | Duplicate security symbol | Validation | — | Sample account with IBM listed twice | Rejected: error names the duplicated symbol | ✔ `TC-18` |
| TC-19 | Empty holdings list | Validation | — | Account with $100,000 and no securities | Rejected: error states the account must contain at least one holding | ✔ `TC-19` |
| TC-20 | Negative percentage | Validation | — | Sample account, but IBM target = −20 (and separately current = −10) | Rejected: error states percentages cannot be negative | ✔ `TC-20` |

**Notation:** `A 20/10 @150` = security A, target 20%, current 10%, unit price $150.

**Traceability:** the `Automated` column gives the pytest test ID prefix; run `python -m pytest -v` and match IDs (e.g. `TC-05-sub-share-variance`). All 22 cases are automated; this catalog stands alone as the manual-execution script.
