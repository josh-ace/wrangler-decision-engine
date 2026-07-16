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
2. **Trim + config** — Sport, Sport S, Willys, Sahara (4dr only), Rubicon, Rubicon X · 2dr vs 4dr · powertrain (V6 6MT · V6 8AT 4dr-only · 2.0T 8AT; **4xe used-only**)
3. **Sourcing channel** — local dealer · out-of-state bulk / national-delivery discount (Mark Dodge, Granger, Koons, Criswell, Aventura) · broker · private
4. **Acquisition finance** — cash · finance · lease
5. **Timing** — order now for delivery · buy off lot now · **MY2026 end-of-run** · wait for **MY2027** (facelift + Hurricane I6 re-power)

**Scope exclusions:**
- **392 (V8 top-of-line)** — out entirely
- **New 4xe** — not in 2026 US order guides; user does not intend to buy new
- **4xe is in-scope only as a used-market scenario** (see Tier 2)

**Legal combinations tracked:** Not every combination is valid. Engine enforces combination constraints (e.g., out-of-state + lease often blocked; manual only with V6; §30D federal credit no longer applies to any scenario — see finding #1).

## TCO framework

All scenarios resolve through the same equation:

```
Total cost to own target build for N years =
    acquisition
  + mods needed to reach target build
  + operating (fuel + insurance + maintenance + tax/reg)
  − exit value at N
  + risk-adjusted expected costs   (see "Risk modeling")
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
- **Risk exposure** — qualitative flags from Risk modeling
- Mod install effort remaining

**Applicability is per-scenario**: some metrics are N/A for certain scenarios (e.g., "exit at 36 months" applies to lease only). N/A ≠ zero — matters for any composite score.

Optional composite score renders as secondary view under user-provided weighting. Primary view is the raw profile scorecard.

## Provenance framework (MVP)

Every value in the engine carries at minimum:
- `source` — where the value came from
- `as_of_date` — when it was pulled/verified

Values without evidence are flagged as **assumptions** and enter the assumption log. Sensitivity analysis identifies which assumptions are load-bearing.

Full schema (confidence tiers, sensitivity machinery) — pending task #4.

## Risk modeling approach

Scenarios that carry structural risk (used-modded builds, used-4xe fire recall exposure and class action drift, battery health uncertainty, program-dependent incentives) apply a **three-layer treatment**:

1. **Quantified TCO line items** for risks that can be honestly monetized — expected cost = probability × impact. Examples: HV battery replacement expected value, extended warranty premium for hedge, loss-of-garage-parking cost during park-outside advisories.
2. **Confidence-interval widening** — scenarios with high stochastic risk exposure show a *range* rather than a point estimate. Same mechanism as used-modded scenarios.
3. **Qualitative risk-score column** — for risks that refuse to monetize honestly (fire recall status, class action outcomes, safety perception), a discrete risk column in the scorecard. Doesn't rig the TCO number; shows up alongside so the ranking can't ignore it.

**Rejected: weighted composite risk scores.** False precision.

Formal design (data sources, probability calibration, math specifics, report presentation) is delegated to task #12 (currently scoped to used-4xe risk).

## Design principles

- **MVP over exhaustive.** Build the minimum viable version, iterate. Perfect enumeration and rigor gate nothing important.
- **Graduated inclusion.** Build the cheapest version of each axis that can answer the strategic question. Escalate depth only where the cheap version says it matters.
- **Extensibility.** Assume we haven't identified every variable. New variable classes must bolt on without rework.
- **Session separation.** Strategic decisions live at the strategic hub. Tactical work runs in delegated sub-contexts with bounded scope.
- **No false precision.** Where a value can be honestly monetized, do so. Where it can't, flag qualitatively — don't pretend.

## Findings shaping the engine (discovery pass, 2026-07-15)

Five findings that changed the taxonomy and scenario space:

1. **Federal EV credits (§30D new · §25E used · §45W commercial/lease-passthrough) are dead** — terminated by the One, Big, Beautiful Bill Act (P.L. 119-21) for vehicles acquired after 2025-09-30. Verified at IRS.gov. Any current "$7,500 on a 4xe lease" is manufacturer/dealer cash, NOT a federal credit — model as short-lived program incentive.
2. **National-delivery discount dealers get quantified.** Mark Dodge (LA), Granger (IA) publicly quote ~7% below invoice with price protection, ~10–16 wk lead time. First-class sourcing scenario with measurable delta vs local dealer.
3. **MY2026 = last-of-V6/manual before MY2027 facelift + Hurricane I6 re-power.** Discrete timing scenario — not a "wait a month" question but a "buy this end-of-run vs wait for refreshed pricier next-gen" question.
4. **Recall/defect risk register is a first-class variable class.** Active in 2026: 4xe HV battery fire recall (~228k units, active class action, park-outside guidance), death wobble on 2024–25 stock units, UConnect 5 OTA failures, TPMS recall (~79k units), Sky One-Touch top leaks. Config-conditional risk flags with real TCO and resale consequences.
5. **Powertrain is a cross-cutting central fork.** 3.6 V6 · 2.0T · 4xe carry structurally different reliability, fuel, resale, warranty (4xe HV 8yr/100k), and (formerly) tax profiles. Not a single MSRP delta — the engine reasons across these dimensions.

## Used case — Tier 2 sanity check via Edmunds

**Scope**: model a small set of canonical used scenarios as engine inputs, not a full listing pipeline.

**Data source**: Edmunds
- **True Market Value** — current transaction-price estimates by config
- **True Cost to Own (5-yr)** — depreciation, insurance, fuel, maintenance, repairs, financing, taxes broken out
- **Private-party vs dealer retail** — channel-differentiated used pricing
- **Ask-a-Dealer forum threads** — monthly MF + residuals for new-side lease math

**Canonical used scenarios:**
1. CPO 2023 Rubicon 4dr V6, ~25k mi
2. CPO 2024 Willys 4dr V6, ~15k mi
3. **Used 2023 Rubicon 4xe 4dr, ~20k mi** — the *sole* 4xe scenario in the engine (4xe in-scope only via used market; risk-penalized per task #12)

**Refresh cadence**: monthly.

**Escalation trigger to Tier 1** (full listing analysis): if any used baseline lands within **$3k or 10% monthly** of best new scenario, escalate. Otherwise, used stays out.

**Great-listing manual escape hatch**: if a specific opportunity surfaces mid-decision, evaluate as a one-off using the shared TCO framework. No automation.

## Open strategic locks

Unresolved and gating downstream work:

- **Time horizon (task #1)** — N-year window for TCO comparison (3 / 5 / 8yr)
- **Weighting philosophy (task #2)** — how the report renders tradeoffs; primary vs secondary metrics
- **Provenance framework detail (task #4)** — beyond MVP source + as_of_date

Resolved:

- **4xe scope (task #3)** — in-scope as used-only; new 4xe out; risk-penalized per #12
- **392 scope** — out entirely

## Variable taxonomy (refined by discovery pass 2026-07-15)

Legend: **✚ added** · **✎ corrected/re-scoped** · (unmarked = validated as-is)

| # | Class | What it captures | Status | Primary source(s) | Refresh |
|---|---|---|---|---|---|
| 1 | Config & MSRP | Trim, packages, options, invoice, holdback (~3% MSRP, computable) | ✎ +invoice+holdback | `config/order_guide.json`; jlwranglerforums spreadsheet | Once/MY |
| 2 | Manufacturer incentives | Customer/retail cash, APR subvention, lease cash, loyalty/military/first-responder | ✓ | Jeep.com incentive lookup (ZIP) + CarsDirect + forum deal threads | Monthly |
| 3 | Lease programs | Money factor, residual % by term/mileage/region | ✓ | Edmunds lease megathread; 4xeForums lease thread | Monthly |
| 4 | Real transaction prices | % off MSRP, dealer discount patterns, deal-quality rating | ✎ broaden | CarGurus IMV/Deal Rating; forum deal reports; TrueCar; KBB Fair Purchase Price | On-demand / weekly |
| 5 | Bulk / national-delivery dealer pricing | Advertised % below invoice, price protection, delivery, lead time | ✎ elevated to scenario axis | Mark Dodge (per-VIN, public), Granger, Koons, Criswell, Aventura | On-demand |
| 6 | Depreciation / residual | JL-specific curves; ALG best-in-class residual award; residual % as model input | ✎ +residual-award | iSeeCars; KBB/Edmunds Cost-to-Own; Manheim index (public) | Yearly / monthly index |
| 7 | Fuel economy | Real-world vs EPA, by powertrain; 4xe MPGe + electric range | ✎ +4xe fields | EPA fueleconomy.gov (free API); Fuelly | Once/MY |
| 8 | Insurance | Personalized premium per config; aggregator averages as pre-quote proxy | ✎ +proxy layer | Personalized quote (finalist); The Zebra/ValuePenguin/MoneyGeek | Once/finalist |
| 9 | Maintenance | Scheduled-service intervals (Normal/Severe), by powertrain; typical costs | ✓ | Mopar owner's-manual PDF; RepairPal; KBB schedule | Once/MY |
| 10 | Reliability | Common issues, ratings; recall/TSB register split to #18 | ✎ split | RepairPal, CR (paywall), J.D. Power, NHTSA API, forums | Once + on recall |
| 11 | Tax / reg | Home-state (often county) use tax, out-of-state titling, doc fee (dealer-state), annual personal-property/ad-valorem tax | ✎ +local | State DOR/DMV; WalletHub (property tax); CarEdge (doc fee) | Once + on rule change |
| 12 | Tax credits | **Federal §30D/§25E/§45W EXPIRED (acquired >2025-09-30, P.L. 119-21)**; state PHEV credits only | ✎ MAJOR re-scope | IRS.gov clean-vehicle page; CO Energy Office/DOR; DOE AFDC | On rule change |
| 13 | Mod costs | Parts pricing for target build; install labor = shop quote (not public) | ✎ +labor gap | Quadratec, Northridge4x4, ExtremeTerrain; local shop | On build change |
| 14 | Warranty | Factory terms (3/36, 5/60); 4xe HV battery 8yr/100k; Magnuson-Moss mod interaction | ✎ +MMWA | jeep.com/warranty; FTC (MMWA); Mopar | Once |
| 15 | Inventory / timing | Stock levels, days-on-lot, MY2026→2027 changeover fork | ✎ +MY-changeover | Jeep inventory; dealer sites; TFL/MoparInsiders | Weekly (decision window) |
| 16 | Personal | Budget, credit, mileage, use case, trade-in value, home state/county | ✓ | User | Static |
| 17 | Used market (Tier 2) | TMV, TCO, private-party/dealer values | ✓ | Edmunds; KBB | Monthly |
| **18** | **✚ Recall / defect risk register** | 4xe fire recall, death wobble, UConnect 5, TPMS, Sky-top leaks — config-conditional risk flags | ✚ NEW | NHTSA API; forums; class-action trackers | On-demand + on recall |
| **19** | **✚ Powertrain profile** | 3.6 V6 vs 2.0T vs 4xe as cross-cutting dimension | ✚ NEW (cross-cutting) | Composite of #6–14 keyed by engine | Derived |
| **20** | **✚ Config availability / MY constraints** | Trim×body-style legality, manual-only w/ V6, "Late Availability" combos, axle prerequisites | ✚ NEW | `config/order_guide.json`; MoparInsiders/JeepSpecs | Once/MY |
| **21** | **✚ Emissions / CARB jurisdiction** | CARB vs 49-state config/availability + 4xe battery-warranty extension in CARB states | ✚ NEW | Order guide fine print; CARB; state rules | Once |

## Resolved gaps

The original spec listed 7 gaps to validate. Discovery pass resolved all:

| Original gap | Verdict | Location |
|---|---|---|
| Dealer add-ons & doc fees | Confirmed real; doc fees partly public (CarEdge), add-ons quote-only | Class #11 + on-demand quote |
| Extended warranty pricing | Quote-only (Mopar terms public, price VIN+mileage-gated) | Class #14 (range) |
| GAP insurance mechanics | Quote-only across channels (CU usually cheapest) | Class #8/#14 (range) |
| Opportunity cost of custom-order wait | Real, quantifiable via 10–16 wk lead + price-protection | Class #5 + #15 |
| CARB vs 49-state emissions | Confirmed → promoted to new class #21 | Class #21 |
| Financing gotchas (prepayment, mandatory add-ons) | Quote-only; surfaces at F&I | Class #2/#11 (finalist) |
| Trade-in value modeling | Sourceable (KBB/Edmunds trade-in / private / dealer-retail cuts) | Class #16/#17 |
