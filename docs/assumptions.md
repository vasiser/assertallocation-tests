# Assumptions

The assessment asks that all assumptions be noted explicitly. These are the rules the application (and therefore the test suite) is built on.

1. **Whole shares only, rounded toward zero.** The share count is `floor(|variance value| / unit price)`. A trade therefore never overshoots the target allocation and never spends more cash than the variance justifies; a residual variance strictly smaller than one share's value remains and is accepted. Sample consequence: IBM buys **66** shares (not 66.67 or 67), ORCL sells **45** (not 45.45 or 46).
2. **Sub-share variance → HOLD.** A non-zero variance whose dollar value is smaller than one unit price produces no trade (action HOLD, 0 shares).
3. **Percentages are the input interface.** The application receives exactly what the assessment table shows — total assets, and per security: target %, current %, unit price. Share counts and market values are derived, not inputs. (Deriving current % from held shares × price would be a thin upstream layer — a discussed extension, not built.)
4. **"100% is vested" = fully invested.** Both the target percentages and the current percentages must each sum to exactly 100. There is no cash sleeve in the model. (The alternative reading — vesting schedules — is treated as out of scope.)
5. **No cash account is modeled.** Trades are computed independently per security; leftover cash from rounding (e.g. the $100 not spent on IBM) and sale proceeds are not tracked or redistributed.
6. **No transaction costs, fees, taxes, lot sizes, or minimum trade amounts.**
7. **Prices are a static snapshot** — no price movement during rebalancing; all values in one currency; prices must be strictly positive.
8. **Output shape:** one instruction per input security, in input order, with a non-negative integer share count and an explicit action (BUY / SELL / HOLD) — direction is never encoded as a sign. Securities with no trade still appear (HOLD 0), matching the table shape.
9. **Percentages may be non-integers** (exact decimal values), which enables penny-precision test cases.
10. **Exact decimal arithmetic** (`Decimal`, not binary floats) — 0.1 has no exact binary representation, and rounding rules must be deterministic (see test case TC-08, where float math would produce 99 shares instead of 100).
11. **Zero total assets is accepted** and produces all-HOLD output; negative total assets is rejected.

# Open questions

- **66.67 vs 66:** the prompt never states whether fractional shares are allowed. Chosen: whole shares. Switching to fractional shares is a one-line change (drop the ROUND_DOWN truncation).
- **"(100% is vested)":** interpreted as "fully invested"; could alternatively refer to a vesting schedule on the assets.
- **Input form:** current % vs current share counts/market values as the application's input. Chosen: percentages, as the table presents them.
- **Round toward zero vs round to nearest:** rounding IBM to 67 shares would minimize absolute variance but overshoots the target and costs more cash than the variance justifies. Chosen: never overshoot.
- **Cash neutrality:** must sale proceeds fund the buys? In the sample they happen to net exactly ($9,900 each way), but with independent floor-rounding this is not guaranteed in general. Chosen: trades are independent; no cash constraint.
- **HOLD rows:** should securities with no trade be omitted from the output or reported with 0? Chosen: reported (HOLD 0).
- **Percentage-sum tolerance:** the strict `sum == 100` validation rejects natural equal splits that cannot be represented exactly in decimals — e.g. three securities at 33.33% sum to 99.99 and are rejected. A tolerance-based check (accept within ±0.01) is the alternative; chosen: strict equality, since the upstream system owns producing consistent percentages.
