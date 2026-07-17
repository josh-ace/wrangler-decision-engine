# Used-4xe Risk Penalty Model — Design Proposal

**Workflow prompt #12 · Branch `4xe-risk-model` · 2026-07-16**
**Scope:** the sole in-scope 4xe scenario — *Used 2023 Rubicon 4xe 4dr, ~20k mi* (spec, "Used case — Tier 2"). Design only; no data collected. New-4xe risk not modeled.

> **Reading the numbers.** This document contains almost no dollar figures on purpose. Where calibration data doesn't exist yet, the proposal specifies the *parameter*, the *source*, and the *calibration procedure*, and registers an assumption ID (`A-nn`) — per spec's "No false precision." Symbolic parameters are `snake_case`. Nothing here is a result.

---

## 0. Thesis — the warranty clock drives the whole model

Almost every 4xe-specific risk resolves through one variable: **time remaining on the 8yr/100k HV battery warranty**, and whether the horizon `N` ends before or after it.

A 2023 4xe entering service ~mid-2023, bought 2026-07 at 20k mi, has **~5 years / 80k mi of HV coverage left**. At any plausible annual mileage (`miles_per_year` ≤ 16k), **time binds before mileage** — coverage lapses ~2031 regardless of driving. So:

| Hold | Exit | HV coverage during hold | Sold as | Battery risk borne by |
|---|---|---|---|---|
| **N=3** | 2029 | fully covered | 6yr old, ~2yr coverage left | Stellantis |
| **N=5** | 2031 | covered; expires at exit | 8yr old, coverage exhausted | Stellantis, but exit lands *on the cliff* |
| **N=8** | 2034 | **years ~5–8 uncovered** | 11yr old, no coverage | **Owner** |

**Consequence:** at N=3 the honest monetized battery-replacement line is ≈ **$0** — a failure inside warranty is Stellantis's bill, not the owner's. The penalty at N=3/N=5 lives almost entirely in **exit value** and the **qualitative column**, not in a repair line. Only at N=8 does a replacement line item become real.

This makes the horizon lock (**task #1**) the single largest determinant of the used-4xe penalty. Flagging that back to the hub: *#12 cannot produce a point answer until #1 resolves; it produces a function of N.*

Two structural notes that shape everything below:

- **Anti-double-count rule.** Resale/exit-value and risk line items both express "the battery is a liability." Each dollar belongs to exactly one. **Rule: the exit-value term captures what the *market* prices in; risk line items capture only *owner-borne out-of-pocket events*.** Degradation that depresses resale is an exit-value effect, not a repair line.
- **Today's price already contains the repeal.** §30D/§25E died 2025-09-30 (P.L. 119-21). A used 4xe priced in 2026-07 has already repriced. The forward risk is **not** "prices will fall" — it's the *shape of the curve from here*, which is an interval problem, not a point-penalty problem.

---

## 1. Data-sourcing plan

| # | Data point needed | Best source(s) | Access | Cadence | Conf. | Treatment |
|---|---|---|---|---|---|---|
| **1.1** | **In-service date + HV warranty expiry for the specific VIN** — the master variable | Jeep owner Dashboard VIN lookup; dealer service dept; Mopar | VIN-gated; dealer confirm | Once per listing | HIGH (obtainable) | **Gate input** — feeds every line |
| **1.2** | Does HV/emissions warranty **transfer to 2nd owner** | jeep.com/warranty; Mopar warranty booklet for MY2023 | Public + booklet | Once | MEDIUM — **verify** (`A-01`) | Gate; if no → scenario changes materially |
| **1.3** | **CARB battery warranty extension** (10yr/150k shape) applicability | CARB regs; MY2023 warranty booklet; VIN emissions cert label | Public + VIN | Once | MEDIUM (`A-02`) | Modifier on 1.1 |
| **1.4** | Whether coverage follows **vehicle certification or registration state** | Warranty booklet; CARB | Public | Once | **LOW — verify** (`A-03`) | Modifier; see §7 |
| **1.5** | HV battery **replacement cost** (pack + labor, out-of-warranty) | Dealer parts quote (VIN); 4xeForums owner reports | Quote-only | On-demand | MEDIUM | **Monetizable** (N=8 only) |
| **1.6** | **Degradation curve** — usable kWh / EV range vs age & miles | 4xeForums degradation threads; owner-reported range logs; Fuelly (4xe rows) | Public read (**403 to scripted GET** — manual) | Once + annual | LOW–MEDIUM (`A-04`) | Monetizable (small, via fuel) + interval |
| **1.7** | **Failure/replacement rate** for 4xe HV packs, by age | NHTSA complaints API (component = electrical/propulsion battery); forums | Free API, no key | On-demand | LOW for *rate* (`A-05`) | Interval + qualitative; **not** a point EV |
| **1.8** | **Fire recall campaign(s)** — MY/VIN range, remedy, park-outside status | **NHTSA `api.nhtsa.gov` recalls + `vpic` VIN decode**; nhtsa.gov/recalls VIN check | Free API, no key | On-demand + on recall | HIGH | **Gate (binary)** + qualitative |
| **1.9** | **Remedy completion status of this VIN** | NHTSA VIN recall check; dealer service history | Public VIN check | Per listing | HIGH | Gate (binary) |
| **1.10** | **Class action status / payout** | TopClassActions; law-firm trackers; PACER | Public | On filing | MEDIUM (status), **LOW ($)** | **$0 in base case** — qualitative upside note |
| **1.11** | **Used 4xe resale trajectory** vs V6 baseline | Edmunds TMV (4xe vs V6, same trim/miles); KBB; iSeeCars (has **separate 4xe rows**); Manheim public index (context only) | Public; Edmunds **403s scripted GET** | Monthly | MEDIUM (`A-06`) | **Exit value + interval** |
| **1.12** | §25E used credit status | **IRS.gov clean-vehicle page** | Public | On rule change | HIGH | **Explicit $0 line** (see §2.4) |
| **1.13** | **HV battery state-of-health diagnostic** — does one exist below dealer level? cost? | Stellantis **wiTECH** (dealer tool, reads pack SOH/cell balance/DTCs); indie hybrid shops; OBD2 apps w/ custom PIDs | Dealer ~1hr diag; indie rare | Per listing | **LOW — this is a research task, not a known** (`A-07`) | **Interval collapser** — see §3.2 |
| **1.14** | User's **home charging** capability + duty cycle | User (class #16) | — | Static | HIGH | **Gate** — see §5 |
| **1.15** | User's **parking substitution cost** if park-outside applies | User | — | Static | HIGH | Conditional monetization (§2.3) |

**Free structured APIs available: NHTSA only.** Everything else is HTML, 403-gated, or quote-only — consistent with discovery §4.

---

## 2. Monetized TCO line items

Contract: each returns a **delta** to the base TCO owned by #8. All are `0` unless the stated gate opens.

### 2.1 HV battery replacement (out-of-warranty only)

```
E[battery_replacement] = P(fail_oow | N) × (pack_cost + labor − salvage_credit)
```

- `P(fail_oow | N)` = probability of a pack failure occurring **after** `warranty_expiry` **and before** exit at N.
- **N=3, N=5 → the term is structurally 0.** The hold ends at/before expiry. Do not fabricate a penalty here.
- **N=8 → nonzero**, over the ~3 uncovered years (vehicle age 8–11).
- **Calibration:** `A-05`. There is no public actuarial table for 4xe pack survival. Calibrate from NHTSA complaint counts (propulsion-battery component) ÷ registered 4xe population as a **lower bound on failure rate** (complaints undercount), cross-read against 4xeForums replacement reports. **Do not present a point EV from this** — carry it as a range and let §3 widen the interval.
- **Expected-value range: not computable pre-calibration.** What is honestly stateable now: bounded above by `pack_cost + labor` (i.e. P=1) and below by 0; and **exactly 0 for N≤5**. Report the N=8 value as a range once `A-05` is calibrated, with `P` shown explicitly, never buried.

### 2.2 Degradation → fuel cost (not a repair)

Capacity fade doesn't produce a bill; it produces **fewer EV miles**, silently shifting miles to gasoline.

```
Δfuel(t) = ev_miles_lost(t) × (cost_per_mi_gas − cost_per_mi_elec)
where ev_miles_lost(t) = ev_range_new × fade_frac(age_t, miles_t) × charge_events(t)
```

- `fade_frac` from `A-04`; `cost_per_mi_*` from EPA fueleconomy.gov (free API: MPGe, gas-only MPG, kWh/100mi) + user's electricity/gas rates.
- **Honest, small, and computable.** Include it — it's the one battery effect that is genuinely monetizable at every N.
- **Gate:** zero if `home_charging = false` (§5) — you can't lose EV miles you were never getting.

### 2.3 Park-outside advisory → parking substitution

```
E[parking_cost] = P(advisory_active_at_purchase | VIN) × advisory_months × monthly_parking_substitution
```

- `P(...)` is **not a probability — it's a lookup** (1.8/1.9). Known at purchase per VIN.
- `monthly_parking_substitution` is a **user input** (1.15). For a driveway owner it is **$0** — and the real cost (fire risk to a structure, hassle) is *not* monetizable → §4.
- **Only monetize when the user supplies a real substitution cost.** Otherwise this line is $0 and the risk lives in the qualitative column. Spec lists this as a candidate monetized line; it qualifies *conditionally*, not by default.

### 2.4 §25E used federal credit — an explicit zero

```
used_federal_credit = 0    # source: IRS.gov; P.L. 119-21; acquired > 2025-09-30
```

Not a risk — a **stale-data guard**. Discovery finding #1 flags that dealer/blog copy still advertises credits that no longer exist. This line exists so the engine states $0 *with provenance* rather than leaving a gap someone fills with $4,000.

**It does not differentiate.** §25E was EV/PHEV-only, so the CPO V6 baselines never had it either — it's $0 across every used scenario. Its effect is **counterfactual**: it removes an advantage used-4xe *would* have held pre-repeal. State that in the report narrative; do not book it as a penalty (that would double-count against §2.5, where the market has already priced it).

### 2.5 Exit value — where the real 4xe penalty lives

Not a "risk line item"; it's the base TCO's exit term, but 4xe-conditional. Two mechanisms the generic curve misses:

1. **Post-repeal repricing** — already in today's acquisition price. Not a forward penalty.
2. **Warranty-cliff aversion at resale** — a 2023 4xe sold at **N=5 (2031)** is 8 years old with HV coverage *exhausted*, sold to a buyer who must self-insure the pack. There is a plausible discount cliff at that boundary. **This is the 4xe-specific resale mechanism** — and it lands exactly on the N=5 exit.

Treat mechanism 2 as an **asymmetric interval** (§3), **not** a point penalty. We do not have the data to price the cliff (`A-06`), and inventing a percentage would be precisely the false precision the spec rejects.

---

## 3. Interval-widening logic

Per spec layer 2: high-stochastic-risk scenarios show a **range**, not a point.

### 3.1 What widens, and why

| Uncertainty | Term widened | Direction | Rationale |
|---|---|---|---|
| Resale cliff at warranty expiry (`A-06`) | **Exit value at N** | **Asymmetric — downside only** | Upside is bounded (4xe won't out-retain a V6 Rubicon; 2026 Wrangler holds the ALG best-in-class award on the *gas* side). Downside is open. |
| Battery SOH unknown on this unit (`A-07` unresolved) | Exit value **+** §2.2 fuel | Two-sided | A healthy pack is genuinely fine; a degraded one is worse on both. |
| Pack failure rate (`A-05`) | §2.1, **N=8 only** | Downside | Thin data; complaint-derived rates undercount. |
| Class-action outcome | **None** — see §4 | — | Upside-only, unknowable timing/amount. $0 base case. |
| Recall re-expansion / new campaign | **None** — see §4 | — | Cannot be honestly distributed. Qualitative. |

### 3.2 The magnitudes — deliberately unspecified

**Every widening factor here is an `A-nn` assumption pending calibration.** Proposing "widen exit value by ±X%" today would be invention. The *procedure*:

1. Calibrate `A-06` from Edmunds/KBB 4xe-vs-V6 spreads at matched trim/mileage across the 8-year-old cohort → an **empirical** cliff estimate.
2. Set interval half-widths from the observed dispersion of that spread, not from judgment.
3. Until then, the used-4xe row renders **"interval pending calibration (`A-06`)"** — an honest blank beats a fabricated band.

### 3.3 Interval collapse via diagnostic (`A-07`) — the value-of-information move

The SOH-unknown widening (row 2) is the one uncertainty a **small certain cost can buy out**. A dealer wiTECH HV diagnostic reads pack state-of-health directly.

**Design it as a conditional gate, not a line item:** if used-4xe ranks within the spec's escalation band (**within $3k or 10% monthly** of the best new scenario), spend the diagnostic fee and re-run with a measured SOH. A ~$150–200-shape diagnostic (**unverified — `A-07`**) collapsing a multi-thousand-dollar interval is trivially worth it; below the band it's wasted effort.

**`A-07` is a genuine open research question, not a known.** Whether a sub-dealer path exists (indie hybrid shops are Toyota/Honda-centric; OBD2 apps with custom PIDs are unverified for the 4xe's pack) needs a real answer before this gate is implementable.

---

## 4. Qualitative risk column entries

Spec layer 3. These **do not touch the TCO number** — they sit beside it so the ranking can't quietly ignore them. Discrete flags, no weighting, no composite (spec: rejected).

| Flag | Value | Phrasing in the scorecard |
|---|---|---|
| **Fire recall** | `remedied` / `open` / `advisory-active` / `n/a` | "Subject to HV battery fire recall; remedy [status] as of [date]. Park-outside guidance [active/lifted]. Fires reported after an earlier software remedy." |
| **Safety valence** | `elevated` | "Catastrophic-loss mode (vehicle fire) is insurable but not fully compensable — garage/structure exposure not modeled in TCO." |
| **Class action** | `active` / `settled` / `none` | "Active battery-defect litigation. Any recovery is **upside, not modeled** ($0 base case); timing and amount unknowable." |
| **Recall re-expansion** | `possible` | "Campaign expanded once (Nov 2025, ~228k units). Further expansion is possible and not distributable — carried as a flag, not a probability." |
| **Battery SOH** | `unmeasured` / `measured: X%` | "Pack health unmeasured on this unit; see diagnostic gate (§3.3)." |
| **Warranty cliff** | `pre-cliff` / `at-cliff` / `post-cliff` | "HV coverage expires ~[date] (vehicle age ~8). Exit at N=[n] lands [before/at/after] the cliff." |
| **Powertrain complexity** | `elevated` | "4xe carries the most failure points of the three powertrains; thinnest independent-service ecosystem (community read: V6 = wheel-to-200k baseline)." |

**Why fire risk stays qualitative:** the owner-borne cost of a fire is roughly a comprehensive-insurance deductible — monetizing it would produce a *trivially small* number that reads as "fire risk ≈ $500," which is worse than useless. The spec anticipated exactly this ("risks that refuse to monetize honestly").

**Why the class action stays at $0:** it's a *credit*. Booking an EV recovery would make the risk-heavy scenario score *better* — perverse. Model $0, note the upside.

---

## 5. Sensitivity flags

Ranked by expected leverage on the used-4xe ranking.

| # | Input | Move | Effect | Note |
|---|---|---|---|---|
| **1** | **`home_charging` (user)** | true → false | **Collapses the entire 4xe thesis** | Without home charging the 4xe is a heavier, more complex V6 with worse everything and no operating offset. **This is a gate, not a sensitivity** — if false, drop the scenario. Not a risk factor; the highest-leverage input in the module. |
| **2** | **Horizon `N` (task #1)** | 5 → 8 | **Step change**, not a gradient | Crosses the warranty cliff: activates §2.1 and widens §3.1 sharply. |
| **3** | **Exit value at N** | ±10% | Largest **absolute** dollar term | Dominates every risk line combined. Where `A-06` calibration must be spent. |
| **4** | **Acquisition delta vs CPO V6** | ±$3k | Direct rank flip | The post-repeal discount is 4xe's *only* structural advantage. If it exceeds the risk penalty, 4xe wins on cost — the model must be able to say so. |
| **5** | **CARB extension applies** (`A-02`/`A-03`) | false → true | Pushes cliff to ~2033/150k | Neutralizes §2.1 even at N=8 and softens §3.1. Binary, user-state-keyed, **high leverage**. |
| **6** | **Recall remedy status** | remedied → open | No TCO change; **flag flips** | By design — the qualitative column carries it. |
| **7** | `pack_cost` (`A-05`) | ±25% | Small at N≤5 (×0), moderate at N=8 | Low priority until #1 locks. |

**Read:** items 1–2 are *gates* the hub must resolve; 3–5 are where calibration effort belongs. Items 6–7 are cheap.

---

## 6. Implementation sketch — interface for #8

### 6.1 Data file — `risk/used_4xe.json`

Follows `config/order_guide.json` conventions: `schema_version`, provenance block, explicit `null` + `notes` for unknowns.

```json
{
  "schema_version": "1.0",
  "provenance": { "source": "4xe_risk_module", "as_of_date": "2026-07-16",
                  "compiled_by": "workflow_12" },
  "warranty": {
    "hv_battery_federal": { "years": 8, "miles": 100000,
      "source": "jeep.com/warranty", "as_of_date": null,
      "transfers_to_second_owner": null, "notes": "A-01 unverified" },
    "carb_extension": { "years": null, "miles": null, "applies_if": null,
      "keyed_to": "vehicle_emissions_certification | registration_state",
      "notes": "A-02/A-03 unverified — see §7" }
  },
  "parameters": {
    "pack_replacement_cost":  { "value": null, "unit": "USD", "assumption_id": "A-05",
                                "source": null, "calibration": "dealer VIN parts quote + 4xeForums reports" },
    "fade_frac_curve":        { "value": null, "assumption_id": "A-04",
                                "calibration": "4xeForums range logs; manual collection (403)" },
    "p_fail_oow_by_age":      { "value": null, "assumption_id": "A-05",
                                "calibration": "NHTSA complaints / registered population = LOWER BOUND" },
    "resale_cliff_spread":    { "value": null, "assumption_id": "A-06",
                                "calibration": "Edmunds/KBB 4xe-vs-V6 spread, 8yr-old cohort, matched trim+miles" },
    "soh_diagnostic_cost":    { "value": null, "assumption_id": "A-07",
                                "calibration": "dealer wiTECH quote; indie-shop availability UNKNOWN" }
  },
  "static_zeros": {
    "used_federal_credit_25E": { "value": 0, "source": "irs.gov/clean-vehicle-tax-credits",
      "as_of_date": "2026-07-13",
      "notes": "Terminated by P.L. 119-21 for vehicles acquired after 2025-09-30. Explicit zero, not a gap." }
  },
  "recall_register_ref": "risk/recall_register.json"
}
```

### 6.2 Function signature

```python
def assess_used_4xe_risk(
    listing: Listing,          # VIN, MY, miles, price, in_service_date
    user: UserProfile,         # home_charging, state, miles_per_year, parking_substitution_cost
    horizon_years: int,        # from task #1 — REQUIRED, model is a function of N
    data: Used4xeRiskData,     # risk/used_4xe.json
) -> RiskAssessment
```

```python
@dataclass
class RiskAssessment:
    gates:                list[Gate]           # e.g. home_charging=False -> scenario dropped
    tco_line_items:       list[LineItem]       # deltas only; #8 owns base TCO
    interval_adjustments: list[IntervalAdj]    # target term + lo/hi half-widths, asymmetric
    qualitative_flags:    list[Flag]           # §4 — never enter the TCO number
    assumptions:          list[AssumptionRef]  # A-01..A-07 touched by this run
    uncalibrated:         list[str]            # params still null -> report renders "pending"
```

```python
@dataclass
class LineItem:
    name: str; value: float | None; monetized: bool
    formula: str                                # human-readable, shown in the engine
    probability: float | None                   # surfaced explicitly, never buried
    provenance: Provenance; assumption_ids: list[str]

@dataclass
class IntervalAdj:
    target_term: str                            # "exit_value" | "fuel"
    lo_delta: float; hi_delta: float            # asymmetric by design
    reason: str; assumption_ids: list[str]
```

### 6.3 Contract rules for #8

1. **Risk module returns deltas.** #8 owns the base TCO equation; this module never rewrites it.
2. **Anti-double-count:** exit-value effects go to `interval_adjustments` (target `exit_value`), never to `tco_line_items`. §0.
3. **Gates run first.** A closed gate drops the scenario — no partial scoring.
4. **`uncalibrated` is not empty → the report renders a range or "pending," never a point.** Enforced, not advisory.
5. **`qualitative_flags` never reach the composite.** Spec: weighted composite risk scores are rejected.
6. **N is required.** No default. The model is a function of N (§0).

---

## 7. Assumption register — validate before calibration

| ID | Assumption | Why it matters | How to validate |
|---|---|---|---|
| `A-01` | HV/emissions warranty transfers to 2nd owner | If false, the entire §0 thesis inverts | MY2023 Mopar warranty booklet |
| `A-02` | CARB extension is 10yr/150k-shaped for MY2023 4xe | Sensitivity #5 | CARB regs + booklet |
| `A-03` | **Coverage keys to the vehicle's emissions certification, not the buyer's registration state** | A 49-state-certified 4xe bought by a CA buyer may get **no** CARB extension — silently breaks #5 | Warranty booklet + VIN emissions cert label |
| `A-04` | 4xe fade curve derivable from owner range logs | §2.2 + interval | 4xeForums (manual; 403) |
| `A-05` | Pack failure rate estimable from complaints ÷ population | §2.1 at N=8 | NHTSA API — **lower bound only** |
| `A-06` | An 8-yr-old 4xe-vs-V6 resale spread is observable today | §3 magnitudes — highest-value calibration | Edmunds/KBB matched cohort |
| `A-07` | A sub-dealer HV SOH diagnostic exists at a knowable cost | §3.3 gate | wiTECH quote; indie-shop survey |

**`A-03` is the sleeper.** It's the one that looks settled and probably isn't.

---

## 8. Back to the hub

1. **Task #1 (horizon) gates this module.** N=3/5 vs N=8 is a step change, not a gradient. #12 cannot produce a point answer until #1 locks.
2. **Add a gate question to class #16 (personal): home charging.** It's higher-leverage than every risk parameter here and it isn't currently captured.
3. **`A-06` is where calibration budget should go** — the exit-value term dominates every risk line combined.
4. **Ready for #8** as specified; §6 is the consumable interface.

*End of proposal.*
