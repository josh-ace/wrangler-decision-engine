# Wrangler Decision Engine — Spec

## Goal

Make the best 2026 Jeep Wrangler purchase decision, defensibly, using a system that can be re-run as market conditions change — not a folder of research that goes stale.

## Two artifacts

1. **Engine** — reproducible model. Inputs + calculations + assumption log + provenance + sensitivity analysis. Editable, versioned.
2. **Report** — the one artifact the user acts on. Ranks scenarios, names a recommendation, exposes the reasoning, flags what would flip the ranking.

The report is the deliverable. The engine is what makes the report defensible and re-runnable.

## Multi-axis scenario framework

Each scenario is a full stack across five axes:

1. **Vehicle condition** — new custom order · new dealer stock · CPO · used private · used dealer
2. **Trim + config** — Sport S, Willys, Sahara, Rubicon, Rubicon X, 392 · 2dr vs 4dr · powertrain (V6, 2.0T, 4xe)
3. **Sourcing channel** — local dealer · out-of-state bulk (Mark Dodge, Koons, Criswell, Aventura) · broker · private
4. **Acquisition finance** — cash · finance · lease
5. **Timing** — order now for delivery · buy off lot now · wait for Q4 clearance · wait for MY27

Not every combination is legal (e.g., out-of-state + lease is often blocked; 4xe federal credit is new-only). Engine tracks combination constraints.

## TCO framework

All scenarios resolve through the same equation:

```
Total cost to own target build for N years =
    acquisition
  + mods needed to reach target build
  + operating (fuel + insurance + maintenance + tax/reg)
  − exit value at N
```

- **New scenarios** = specification (build this, buy this way)
- **Used scenarios** = listing (this specific unit, priced today)

Both populate the same equation with different data schemas.

## Report shape

**Scorecard of scenario profiles**, not a single composite. Rows are scenarios; columns are metrics.

**Financial metrics per scenario:**
- N-year total cost of ownership
- Monthly cash flow
- Upfront cash required
- Exit value at horizon
- Cost per mile
- Delta vs cheapest scenario

**Non-financial metrics per scenario:**
- Time to acquire
- Warranty coverage at horizon
- Exit flexibility
- Configuration precision
- Risk exposure
- Mod install effort remaining

**Applicability is per-scenario**: some metrics are N/A for certain scenarios (e.g., "exit at 36 months" applies to lease only). N/A ≠ zero — matters for any composite score.

Optional composite score renders as secondary view under user-provided weighting. Primary view is the raw profile scorecard.

## Provenance framework (MVP)

Every value in the engine carries at minimum:
- `source` — where the value came from
- `as_of_date` — when it was pulled/verified

Values without evidence are flagged as **assumptions** and enter the assumption log. Sensitivity analysis (later) identifies which assumptions are load-bearing enough to be worth validating.

Full schema (confidence tiers, sensitivity machinery) — TBD.

## Design principles

- **MVP over exhaustive.** Build the minimum viable version, iterate. Perfect enumeration and rigor gate nothing important.
- **Graduated inclusion.** Build the cheapest version of each axis that can answer the strategic question. Escalate depth only where the cheap version says it matters.
- **Extensibility.** Assume we haven't identified every variable. New variable classes must bolt on without rework.
- **Session separation.** Strategic decisions live at the hub. Tactical work runs in delegated sub-contexts with bounded scope.

## Used case — Tier 2 sanity check via Edmunds

**Scope**: model a small set of canonical used scenarios as engine inputs, not a full listing pipeline.

**Data source**: Edmunds
- **True Market Value** — current transaction-price estimates by config
- **True Cost to Own (5-yr)** — depreciation, insurance, fuel, maintenance, repairs, financing, taxes broken out
- **Private-party vs dealer retail** — channel-differentiated used pricing
- **Ask-a-Dealer forum threads** — monthly MF + residuals for new-side lease math

**Canonical used scenarios to model:**
1. CPO 2023 Rubicon 4dr V6, ~25k mi
2. CPO 2024 Willys 4dr V6, ~15k mi
3. Used 2023 Rubicon 4xe 4dr, ~20k mi (only if 4xe in scope)

**Refresh cadence**: monthly

**Escalation trigger to Tier 1** (full listing analysis): if any used baseline lands within **$3k or 10% monthly** of best new scenario, escalate. Otherwise, used stays out.

**Great-listing manual escape hatch**: if a specific opportunity surfaces mid-decision, evaluate as a one-off using the shared TCO framework. No automation.

## Open strategic locks

The following are unresolved and gate downstream work:

- **Time horizon** — N-year window for TCO comparison (3 / 5 / 8yr)
- **Weighting philosophy** — how the report renders tradeoffs; primary vs secondary metrics
- **4xe scope** — in or out of scenario space
- **Provenance framework detail** — beyond MVP source + as_of_date

## Variable taxonomy (draft — to be refined by discovery pass)

| Class | What | Source (proposed) | Refresh |
|---|---|---|---|
| Config & MSRP | Trim, packages, options, invoice math | Order guide PDFs | Once per MY |
| Manufacturer incentives | Customer cash, APR subvention, lease cash, loyalty/military | Jeep.com + CarsDirect + Stellantis dealer bulletins | Monthly |
| Lease programs | Money factor, residuals by term/mileage/region | Edmunds Ask-a-Dealer forum | Monthly |
| Real transaction prices | % off MSRP, dealer discount patterns | Forum deal reports, CarGurus, TrueCar | On demand |
| Bulk dealer pricing | Mark Dodge / Koons / Criswell / Aventura quotes | Direct quote | On demand |
| Depreciation | JL-specific curves | iSeeCars, KBB, Manheim reports | Yearly |
| Fuel economy | Real-world vs EPA | Fuelly, forums | Once |
| Insurance | Personalized quote per config | Direct insurer quote | Once per finalist |
| Maintenance | Schedule + typical costs | Jeep manuals, RepairPal, CR | Once |
| Reliability | Common issues, recall history | CR, JD Power, forums | Once |
| Tax/reg | Sales tax mechanics, out-of-state title rules, personal property tax | State DMV, CPA rules | Once + on rule change |
| Tax credits | 4xe federal §30D income cap, MSRP cap, sourcing rules; state EV credits | IRS, state DOR | On rule change |
| Mod costs | Parts + install labor for target build | Northridge4x4 / Quadratec, local shop rates | On build change |
| Warranty impact | What mods void what | Jeep warranty terms, forums | Once |
| Inventory/timing | Stock levels, days-on-lot, MY changeover | Jeep inventory, dealer sites | Weekly during decision window |
| Personal | Budget, credit, mileage, use case, trade-in value | User | Static |
| Used market (Tier 2) | TMV, TCO, private-party/dealer values | Edmunds | Monthly |

**Known gaps to validate:**
- Dealer add-ons and doc fees (state-regulated)
- Extended warranty pricing
- GAP insurance mechanics
- Opportunity cost of custom-order wait
- CARB vs 49-state emissions differences
- Financing gotchas (prepayment penalties, mandatory add-ons)
- Trade-in value modeling
