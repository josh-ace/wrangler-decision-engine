# Wrangler Decision Engine — Spec

## Goal

Make the true cost structure of a 2026 Jeep Wrangler purchase visible, so the answer becomes intuitive without needing years of experience to read pricing sheets. The tool decomposes the decision into layers, sizes each price-affecting lever in dollars, and exposes the value structure at every level. Not a ranking, not a recommendation — a decomposition that lets the user see the answer.

## Two artifacts

1. **Engine (Python)** — data loader + renderer. Parses raw sources, fetches market data, renders the .xlsx, merges refreshes. Does *not* run calculations at use-time. See "Implementation architecture" below.
2. **Report (multi-tab .xlsx)** — the one artifact the user reads and works out of. All calculations live as Excel formulas in the file. Decomposes the decision layer by layer, sizes each lever in dollars, exposes the value structure per layer. No ranking, no composite score — transparency. Self-contained; portable; user never needs Python to *use* the tool.

The .xlsx is the deliverable. Python is the mechanism for producing and updating it.

## Implementation architecture

**Python is a data loader and renderer, not a runtime engine.** Once the .xlsx is rendered, it's a self-contained tool — Excel formulas drive all calculations; the user never needs Python to *use* the tool, only to refresh market data. Push calculations into Excel; keep Python's role minimal.

### Division of labor

**Python** does:
- Parse raw sources (order guides, IRS pages, forum threads) into structured JSON/YAML
- Fetch/scrape market data on demand (`engine refresh`)
- Initial render of the .xlsx from data + formula scaffolding (`engine render`)
- Refresh writes only into designated `Data_*` tabs; preserves user tabs and analysis tabs

**Excel** does:
- Every calculation via formulas (feature-value math, three-price transparency, sourcing delta, financing mechanism, ongoing costs, sensitivity)
- Formatting and presentation
- Interactive what-if via cell edits
- Provenance display (source + as_of_date visible per value)

**User** does:
- Edits `Inputs` and `Notes` tabs
- Reads analysis tabs
- Runs `engine refresh` only when they want fresh market data

### Discipline: Excel Tables and named ranges

Refresh must not break formulas. All data on Python-owned tabs lives in **Excel Tables** (structured references like `Trims[MSRP]` instead of `$A$2:$A$20`). All single-cell inputs referenced by formulas are **named ranges**. Refresh writes into tables by name — appending or removing rows never breaks downstream references. This discipline is enforced from the initial render.

### Tab structure

Naming convention: `Inputs` and `Notes` (user-owned) · `Data_*` (Python-owned raw data) · `Analysis_*` (Excel-formula-computed) · `Ref_*` (reference / provenance).

**User-owned** (Python never writes):
- `Inputs` — budget, target build capabilities, HYSA rate, down payment, trade-in value, state, ZIP, garaging, horizons to compare, home charging
- `Notes` — free-form user notes

**Python-owned data** (refreshable via `engine refresh`):
- `Data_Trims` — trim × body × powertrain with MSRP, from `config/order_guide.json`
- `Data_Options` — option codes, prices, applies-to-trims
- `Data_Features` — feature taxonomy, availability matrix, three-price data
- `Data_Incentives` — manufacturer incentives + as_of_date
- `Data_Lease` — MF/residual by term/config + as_of_date
- `Data_ModPricing` — feature → parts + install hours + as_of_date
- `Data_Used` — Edmunds TMV/TCO for canonical used entries + as_of_date
- `Data_TaxRules` — state × rate; federal credit status
- `Data_Depreciation` — JL-specific curves

**Excel-computed analysis** (all formulas):
- `Analysis_Levers` — biggest levers sized in $ for the user
- `Analysis_TrimPath` — three-price feature transparency + landed cost per trim path
- `Analysis_Sourcing` — per-channel adjusted price
- `Analysis_Financing` — cash / finance / lease with mechanism visible
- `Analysis_Timing` — incentive delta by timing choice
- `Analysis_OngoingCosts` — fuel/insurance/maintenance/tax per path over user horizon
- `Analysis_Sensitivity` — what would flip which layer

**Reference:**
- `Ref_Provenance` — every data value's source + as_of_date consolidated
- `Ref_Legend` — how to read the tabs

### Tool choices

- **openpyxl** — pure Python, reads/writes .xlsx, preserves formulas
- **`.xlsx`** format (works in Excel, LibreOffice, Numbers)
- CLI: `engine render` (fresh build), `engine refresh` (merge market data)
- Source-of-truth JSON/YAML in `data/`, version-controlled

### Provenance in this architecture

Every value on `Data_*` tabs carries `source` and `as_of_date` per the MVP provenance framework (may render as adjacent columns on the tab or as cell comments). The `Ref_Provenance` tab consolidates them into a single lookup. Excel formulas can reference them; the user can always click a value and see where it came from.

## Multi-axis decision framework

The decision spans five price-affecting axes. Each is a decision layer with its own transparency section in the report:

1. **Vehicle condition** — new custom order · new dealer stock · CPO · used private · used dealer
2. **Trim + config** — Sport, Sport S, Willys, Sahara (4dr only), Rubicon, Rubicon X · 2dr vs 4dr · powertrain (V6 6MT · V6 8AT 4dr-only · 2.0T 8AT; **4xe used-only**)
3. **Sourcing channel** — local dealer · out-of-state bulk / national-delivery discount (Mark Dodge, Granger, Koons, Criswell, Aventura) · broker · private
4. **Acquisition finance** — cash · finance · lease
5. **Timing** — order now for delivery · buy off lot now · **MY2026 end-of-run** · wait for **MY2027** (facelift + Hurricane I6 re-power)

**Scope exclusions:**
- **392 (V8 top-of-line)** — out entirely
- **New 4xe** — not in 2026 US order guides; user does not intend to buy new
- **4xe is in-scope only as a used-market scenario** (see Used case)

**Legal combinations tracked:** Not every combination is valid. Engine enforces combination constraints (e.g., out-of-state + lease often blocked; manual only with V6; §30D federal credit no longer applies to any scenario — see finding #1).

## Cost decomposition framework

The engine's underlying math resolves the total cost of any path (target build × trim × sourcing × financing × timing × condition) over horizon N as:

```
Total cost to reach target build over N years =
    acquisition (trim + config + destination + fees)
  + mods needed to reach target build
  + operating (fuel + insurance + maintenance + tax/reg)
  − exit value at N
  + risk-adjusted expected costs
```

The math is the same as a TCO calculation. What differs is the *output*: the engine doesn't compute a single N-year TCO number per scenario and rank scenarios by it. It decomposes each *decision layer* — trim path, sourcing, financing, timing, ongoing costs — and shows the dollar delta each layer moves. The user sees how each layer contributes to total cost per path, not just a ranked list of scenario totals.

- **New scenarios** = specification (build this config, buy this way)
- **Used scenarios** = listing (this specific unit, priced today)

Both flow through the same equation with different input schemas.

## Report shape

Organized by **decision layer**, not by scenario. Each layer is a tab in the .xlsx (see "Implementation architecture" for tab naming), presenting dollar movement and mechanism through Excel formulas. The five conceptual sections below map to `Analysis_*` tabs.

### 1. Target build (the invariant)

Your capability targets — 35s, rear locker, rock rails, ~2" lift, winch, steel bumper, etc. Capability outcomes, not measurements, not a shopping list. Every path has to reach these.

### 2. Biggest levers for you

A dollar-sized summary of which decision layers move the price most for your specific target build and personal inputs:

```
Trim path:      up to ±$8,200
Sourcing:       up to ±$2,800
Financing:      up to ±$1,900 (current incentive window)
Timing:         up to ±$1,500 (MY26 end-of-run vs wait)
Trade-in:       up to ±$1,200 (private vs dealer credit)
```

Tells the user where the money actually is and where to focus attention. Prioritization as a first-class output.

### 3. Per-layer transparency sections

For each price-affecting axis, a decomposition section. Pattern varies but the shape is *transparency*, not ranking.

**Trim path** — three-price breakdown per feature-delta:

| Feature | Standard-embedded | Factory option | Aftermarket |
|---|---|---|---|
| Rear locker | Rubicon-included | not optionable on Sport/S/Willys | $X installed |
| Rock rails | Willys, Rubicon | $Y on Sport/S | $Z aftermarket |
| Sway disconnect | Rubicon | not optionable elsewhere | $W aftermarket |
| ... | ... | ... | ... |

Plus landed-cost comparison for target build across trim paths (Sport + factory + mods vs Willys + fewer mods vs Rubicon at-target).

**Sourcing** — actual price for the chosen config across channels:

| Channel | Price for target config | Delta vs local | Notes |
|---|---|---|---|
| Local dealer (est. 4% off invoice) | $X | — | — |
| Mark Dodge (~7% off invoice) | $Y | −$D | +price protection, 10–16wk lead |
| CPO 2023 Rubicon similar spec | $Z | −$D' | used-path alternative |

**Financing** — three-way with mechanism visible:

```
Cash               Finance (given incentive)   Lease
─────              ──────────────────────      ─────
$X upfront         $Y/mo × N months            $Z/mo × M months
Keep the car       Keep the car                Walk at exit
Opp cost of tied   Interest paid over term     Effective monthly
cash at your HYSA  Effective vs cash: ±$D      + implied buyout math
rate: $D over N
```

Shows the mechanism, not just the number. If a 0% finance incentive is on the table, the user *sees* why cash may be more expensive than finance.

**Timing** — current-window incentive delta vs waiting:

```
Buy this week: incentives = $X; MDS = Y (low → dealer motivated)
Buy Q4:        expected incentive shift = $Z (based on program history)
Wait MY27:     refresh + Hurricane I6 (~$? premium; V6/manual gone)
```

**Ongoing costs (horizon N)** — decomposed by category, per path where they differ:

| Category | Sport-mods path | Willys-mods path | Rubicon path | Used-CPO path |
|---|---|---|---|---|
| Fuel over N yr | ... | ... | ... | ... |
| Insurance | ... | ... | ... | ... |
| Maintenance | ... | ... | ... | ... |
| Property tax | ... | ... | ... | ... |
| Exit value | ... | ... | ... | ... |

**Risk flags** — shown next to the dollars they affect, not rolled into a composite score:

- 4xe fire recall (2023 in scope): park-outside guidance applicable? Check VIN status.
- Death wobble on 2024–25 stock: qualitative flag on those units.
- UConnect 5 OTA failures: qualitative reliability drag; awaiting Q1 2026 fix.

### 4. Sensitivity — what would change the picture

What input movements would flip which layer's answer. Example:

- If HYSA drops to 1%: cash-vs-finance advantage collapses; sign may flip
- If Mark Dodge lead exceeds 12wk: opportunity cost of the wait eats half the sourcing savings
- If fuel jumps 15%: 2.0T path saves $X vs V6 over 5yr, previously $0 difference

User sees where their answer is stable and where it's fragile.

### 5. Provenance summary

Count of values by source, oldest `as_of_date`, list of assumptions currently unbacked by data. Trust surface.

## Provenance framework (MVP)

Every value in the engine carries at minimum:
- `source` — where the value came from
- `as_of_date` — when it was pulled/verified

**Dataset-citation pattern**: for values sourced from published versioned datasets (EIA AEO fuel-price cases, iSeeCars annual depreciation studies, IRS publication editions), `source` may be structured to name the dataset edition explicitly — e.g., `{type: "published_dataset", name: "AEO 2025 reference case", editor: "EIA", edition: "2025"}`. Preserves the citation past URL rot. Idea from #11 (T3CO's vintage-tagged inputs).

Values without evidence are flagged as **assumptions** and enter the assumption log. Sensitivity analysis identifies which assumptions are load-bearing.

Full schema (confidence tiers, sensitivity machinery, dataset-citation formalization) — pending task #4.

## Risk modeling approach

Scenarios that carry structural risk (used-modded builds, used-4xe fire recall exposure and class action drift, battery health uncertainty, program-dependent incentives) apply a **three-layer treatment**:

1. **Quantified line items** where risk can be honestly monetized — expected cost = probability × impact. These appear in the ongoing-costs decomposition section for the affected path. Examples: HV battery replacement expected value (N=8 only per finding #7), extended warranty premium for hedge, loss-of-garage-parking cost during park-outside advisories.
2. **Confidence-interval widening** for stochastic tail risk — affected paths show a *range* per line item rather than point estimates.
3. **Qualitative risk flags** shown next to the layer they affect — NOT rolled into any composite. If a used-4xe carries a fire recall flag, the flag appears next to the used-4xe sourcing/pricing line so the user sees it in context.

**Rejected: weighted composite risk scores.** False precision. Redundant given no scoring at all under the transparency framing.

**Anti-double-count rule** (from #12): resale/exit-value and risk line items can both express "the asset is a liability." Each dollar belongs to exactly one. Rule: *the exit-value term captures what the market prices in; risk line items capture only owner-borne out-of-pocket events.* Depreciation that depresses resale is an exit-value effect, not a repair line.

Formal design for the used-4xe risk model is complete (`4xe-risk/proposal.md`, workstream #12). Framework generalization for other risk-carrying scenarios pending.

## Design principles

- **Transparency over recommendation.** The tool reveals value structure; the user picks. No ranked winner, no composite score. Every dollar decomposed by layer so the answer becomes visible without trusting a black box.
- **MVP over exhaustive.** Build the minimum viable version, iterate. Perfect enumeration and rigor gate nothing important.
- **Graduated inclusion.** Build the cheapest version of each axis that can answer the strategic question. Escalate depth only where the cheap version says it matters.
- **Extensibility.** Assume we haven't identified every variable. New variable classes must bolt on without rework.
- **Session separation.** Strategic decisions live at the strategic hub. Tactical work runs in delegated sub-contexts with bounded scope.
- **No false precision.** Where a value can be honestly monetized, do so. Where it can't, flag qualitatively — don't pretend.
- **Community-anchored calibration.** Sub-models with well-established community answers (e.g., "Sport + mods vs Rubicon" for the mod-adjusted cost function) must reproduce those answers at their own inputs. Reality-check on math independent of engine abstractions. Idea from #11.

## Findings shaping the engine

1. **Federal EV credits (§30D new · §25E used · §45W commercial/lease-passthrough) are dead** — terminated by the One, Big, Beautiful Bill Act (P.L. 119-21) for vehicles acquired after 2025-09-30. Verified at IRS.gov. Any current "$7,500 on a 4xe lease" is manufacturer/dealer cash, NOT a federal credit — model as short-lived program incentive.
2. **National-delivery discount dealers get quantified.** Mark Dodge (LA), Granger (IA) publicly quote ~7% below invoice with price protection, ~10–16 wk lead time. First-class sourcing layer with measurable delta vs local dealer.
3. **MY2026 = last-of-V6/manual before MY2027 facelift + Hurricane I6 re-power.** Discrete timing layer entry — not a "wait a month" question but "buy this end-of-run vs wait for refreshed pricier next-gen."
4. **Recall/defect risk register is a first-class variable class.** Active in 2026: 4xe HV battery fire recall (~228k units, active class action, park-outside guidance), death wobble on 2024–25 stock units, UConnect 5 OTA failures, TPMS recall (~79k units), Sky One-Touch top leaks. Config-conditional risk flags with real dollar consequences on affected layers.
5. **Powertrain is a cross-cutting central fork.** 3.6 V6 · 2.0T · 4xe carry structurally different reliability, fuel, resale, warranty (4xe HV 8yr/100k), and (formerly) tax profiles. Reasoned across dimensions in the trim/config layer.
6. **Prior art doesn't displace the engine (workstream #11).** Four independent research passes converged: consumer data products price one config; execution services negotiate one deal; the decision layer between them — decomposition transparency — has no occupant at any price point. Verdict: build. Detail: `prior-art/report.md`.
7. **Used-4xe risk penalty is horizon-dependent (workstream #12).** The HV battery warranty clock (8yr/100k) is the master variable. A 2023 4xe bought now at ~20k mi has ~5yr/80k mi of coverage remaining; time binds before mileage. At N=3 the monetized battery-replacement line is structurally $0 (Stellantis's bill); at N=5 the exit lands on the warranty cliff; only at N=8 does an owner-borne replacement line become real. Task #1 (horizon lock) is now the largest single determinant of the used-4xe cost profile. Detail: `4xe-risk/proposal.md`.
8. **Framing shift: transparency system, not recommendation engine (2026-07-17).** Same variables in scope; different output shape. The engine's job is decomposition of the decision into layers with dollar-sized levers, not ranking of scenarios by TCO. User picks; tool reveals. Composite scoring dropped entirely. Weighting philosophy (was open lock #2) is moot. Report structure rewrites to per-decision-layer transparency sections.

## Used case

Used is an alternative *condition/sourcing path* to the target build, not a separate ranking exercise. In the decomposition report, used appears as entries in the condition/sourcing layer alongside new custom order, new stock, CPO, etc. — each with its own price for the target-build config.

**Data source**: Edmunds (True Market Value, True Cost to Own, private-party/dealer values), plus Ask-a-Dealer forum threads for lease MF/residuals on new-side comparisons.

**Canonical used entries to price:**
1. CPO 2023 Rubicon 4dr V6, ~25k mi
2. CPO 2024 Willys 4dr V6, ~15k mi
3. **Used 2023 Rubicon 4xe 4dr, ~20k mi** — sole 4xe entry (4xe in-scope only via used market; risk-flagged per task #12)

**Refresh cadence**: monthly.

**Tier 1 escalation** (full listing analysis): if any used entry lands within **$3k or 10% monthly** of best comparable new path in the decomposition, invest in listing-level analysis; otherwise treat as anchor entry only.

**Great-listing manual escape hatch**: a specific opportunity mid-decision gets evaluated as a one-off through the same cost-decomposition framework.

## Open strategic locks

- **Provenance framework detail (task #4)** — beyond MVP source + as_of_date; schema shapes engine data structures, so this is a genuine architectural lock

Resolved:

- **4xe scope (task #3)** — in-scope as used-only; new 4xe out; risk-flagged per #12
- **392 scope** — out entirely
- **Weighting philosophy** (was task #2) — moot after finding #8 framing shift to transparency. No ranking, nothing to weight. Removed.
- **Report structure** — decomposed by layer per finding #8; no scorecard, no composite
- **Time horizon** (was task #1) — **not a strategic lock; it's a runtime parameter.** Sub-models accept N; report can render one N or compare across N (e.g., N=3 vs N=5 vs N=8, which the used-4xe warranty cliff makes uniquely revealing). Horizon is captured as a field on class #16 (Personal), not a spec-time decision.

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
| 15 | Inventory / timing | Stock levels, days-on-lot, **Market Days Supply (per config; negotiability signal)**, MY2026→2027 changeover fork | ✎ +MDS +MY-changeover | Jeep inventory; dealer sites; CarEdge (MDS); TFL/MoparInsiders | Weekly (decision window) |
| 16 | Personal | Budget, credit, mileage, use case, trade-in value, home state/county, **home charging capability + duty cycle (gate for used-4xe scenario)** | ✎ +charging | User | Static |
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
