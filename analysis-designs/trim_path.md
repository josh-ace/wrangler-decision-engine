# Analysis_TrimPath — design document (IC #4)

Design-only spec for the `Analysis_TrimPath` tab. IC #19 implements this
mechanically: this document fixes the layout, every formula, the new named
ranges, and a worked example carrying real numbers so the implementation can be
validated against ground truth. No code is changed by this IC.

Data grounding (all values used below are pulled from the repo, not invented):

- MSRPs from `config/order_guide.json` via `Data_Trims` (`engine render`).
- Standard-vs-option status from `data/features.json` → `Data_Features`.
- Aftermarket parts + install hours from `data/mod_pricing.json` → `Data_ModPricing`.

Tables the formulas join against (column names verbatim from the data modules):

| Table | Columns (data columns; `Source`, `As_Of_Date` appended by the renderer) |
|---|---|
| `Trims` | `Trim`, `Body`, `Powertrain`, `MSRP`, `Invoice` |
| `Features` | `Feature`, `Category`, `Standard_On`, `Factory_Option_Price`, `Aftermarket_Price` |
| `ModPricing` | `Feature`, `Parts_Cost`, `Install_Hours` |
| `Target_Build` | `Feature`, `Include` — **new**, on `Inputs` (this design) |

`Trims` has 28 configuration rows, `Features` 38, `ModPricing` 20. `Features` and
`ModPricing` join **by `Feature` display name** (mod-pricing rows are already
keyed to the taxonomy's display name in `mod_pricing.py`), which is the join this
tab relies on.

---

## Purpose

The trim-path layer answers one question the community argues about endlessly:
*for the capability you actually want, is it cheaper to buy a cheap trim and mod
up, or to buy a trim that already includes the hardware?* Per spec "Report shape"
§3, the answer is not a ranked winner — it is a **three-price decomposition**. For
each feature in the user's target build, the tab shows whether the feature is
**standard-embedded** on a given trim (cost already in the MSRP), available as a
**factory option** (N/A in MVP — see below), or reachable **aftermarket** (parts +
labor). It then rolls those per-feature facts up into a **landed cost per trim
path** — MSRP plus every aftermarket dollar needed to reach the target build on
that trim — and shows the delta between paths.

The output makes the trade visible without trusting a black box: the user sees
that a Sport reaches the target ~$9k cheaper than an at-target Rubicon *on price
alone*, and sees exactly which mods carry that gap — while the non-price trade-offs
(driveline-mod warranty exposure, resale, time-to-build) live as flags in *other*
layers rather than being blended into one score. Transparency over recommendation.

---

## Target build encoding on Inputs tab

The user's target build is the invariant every trim path must reach (spec §3.1).
It is encoded as a marked list of features on the `Inputs` tab.

### Section on `Inputs`

Below the existing single-cell input block (rows 1–9 after `Input_Labor_Rate` is
added — see "New named ranges"), Python renders a target-build section:

```
(blank spacer row)
A: Target build                         [section header, bold]
A: Mark Include = "Yes" for each capability your build must reach. Every trim
   path's landed cost is computed to hit exactly these. Aftermarket pricing is
   only defined for the features listed here (the ones with a practical
   aftermarket); factory-only trim hardware still shows as standard-embedded
   where a trim includes it.                              [subheader, wrapped]
(blank spacer row)
   Feature                    | Include?
   Rear Locker                | No
   Front Locker               | No
   4.10 Axle Ratio            | No
   ...                        | ...
   Trailer Tow & Hitch Prep   | No
```

### Table structure

An Excel Table named **`Target_Build`** with two columns:

- `Feature` — the taxonomy **display name** (e.g. `Rear Locker`), so it joins
  `Features[Feature]` and `ModPricing[Feature]` by name exactly like the two data
  tabs join each other.
- `Include` — a text cell the user sets to `Yes` / `No`. Data-validated to a
  `Yes,No` dropdown so it reads like a checkbox and can't hold typos the formulas
  would silently miss. Default `No`.

Two columns only — keep it a marking surface, not a data entry burden.

### How Python seeds it on first render

On `engine render`, Python reads `data/mod_pricing.json`, takes every
`feature_id` that has a pricing entry (the 20 covered features), resolves each to
its display name via the same id→name map `mod_pricing.py` already builds, and
writes one `Target_Build` row per covered feature with `Include = "No"`. Seeding
from mod-pricing coverage (not the full 38-feature taxonomy) is deliberate: a
feature with no aftermarket row has no aftermarket landed-cost path, so listing it
as a target the user could "Include" would be misleading. The user marks `Yes` on
the handful they want after opening the file.

### Refresh behavior (the contract: never break selections)

The hard rule: **a refresh must never alter or drop a user's `Include` value.**
`Target_Build` lives on `Inputs`, which `engine refresh` does not write — so in the
MVP implementation selections are preserved trivially (refresh rewrites only
`Data_*`). The only gap this leaves: a feature newly added to `mod_pricing.json`
between renders won't appear as a `Target_Build` row until the next fresh
`engine render`.

**Recommended for IC #19 (MVP):** rely on the render-time seed; do **not** modify
the refresh path. Selections survive every refresh because `Inputs` is untouched.

**Documented target behavior (follow-on IC, not IC #19):** an *additive-only*
merge — refresh may **append** `Target_Build` rows for feature-ids newly present
in `mod_pricing.json`, with `Include = "No"`, and must **never** edit or remove an
existing row or its `Include` value. This is a deliberate, narrowly-scoped
exception to "refresh never writes `Inputs`" and should be its own IC with its own
refresh-preservation test; it is out of scope here so this IC stays additive-safe.

---

## New named ranges required

| Named range | Cell | Default | Purpose |
|---|---|---|---|
| `Input_Labor_Rate` | `Inputs!$B$8` (next free `INPUT_ROWS` row) | `120` | User's shop labor rate ($/hr). Aftermarket labor = install hours × this. The one non-public number in the mod-cost model (no retailer publishes a labor dollar figure), kept as a single user-editable input per `mod_pricing.py`'s design. |

Adding it is a one-line edit to `INPUT_ROWS` in `workbook.py` (append
`("Labor rate ($/hr)", "Input_Labor_Rate")`) plus writing `120` into that value
cell. `_add_named_ranges()` already turns every `INPUT_ROWS` entry into a
workbook-scope named range, so no other change is needed to expose it.

No other new named ranges are required. Everything else the tab needs is reached
through structured table references (`Trims[MSRP]`, `Features[Standard_On]`,
`ModPricing[Parts_Cost]`, `ModPricing[Install_Hours]`, `Target_Build[Feature]`,
`Target_Build[Include]`), which resolve workbook-wide by table name and survive
row add/remove — no cell addresses, no per-column named ranges.

---

## Analysis_TrimPath layout

Two sections on the one tab, each wrapped in its own Excel Table so that
references across and within them are structured (never `$A$2`). The **detail
table is the computational engine** (per config × feature, one line each); the
**summary table aggregates it** with `SUMIFS`. Building it this way — rather than
one giant `SUMPRODUCT` in the summary — keeps every dollar individually visible
(the transparency principle) and keeps the formulas free of array gymnastics.

```
Row 1:  Trim path — three-price transparency + landed cost   [TITLE]
Row 2:  (blank)
Row 3:  SECTION 1 — Landed cost per trim path
Row 4:  [TrimPathSummary table header]
Row 5.. : 28 rows, one per Data_Trims configuration
        Trim | Body | Powertrain | Config_Key | Base_MSRP | Factory_Options_Cost
             | Aftermarket_Cost | Aftermarket_Labor_Cost | Landed_Cost
             | Delta_vs_Cheapest
        (~row 33 is the last config)
Row 35: (blank)
Row 36: SECTION 2 — Per-feature breakdown (three-price detail)
Row 37: [TrimPathDetail table header]
Row 38.. : 28 configs × 20 target-eligible features = 560 rows
        Trim | Body | Powertrain | Feature | Config_Key | Included
             | Standard_On_Trim | Factory_Option_Price | Aftermarket_Parts
             | Aftermarket_Labor | Aftermarket_Total | Parts_Applied
             | Labor_Applied | Contribution_to_Landed
```

**Why 28 × 20 = 560 detail rows (all covered features, not just the marked
ones).** The detail table is written once at render and is refresh-inert (refresh
never touches `Analysis_*`). If it enumerated only the *included* features, its row
count would depend on user selections and would be wrong the moment the user
changed a `Yes`/`No`. Enumerating all 28 configs × all 20 `Target_Build`-eligible
features makes the table static; the `Included` gate (below) zeroes out the rows
whose feature the user didn't mark. 560 formula rows is trivial for Excel.

**Config_Key** = `[@Trim]&" / "&[@Body]&" / "&[@Powertrain]` is present in both
tables and is the join the summary's `SUMIFS` uses to pull each config's
contributions out of the detail. The `Trim` / `Body` / `Powertrain` identity
columns are written by Python as literal enumeration (they are stable join keys
from `Data_Trims`, not computed values); `Base_MSRP` and every dollar column are
formulas, so a refresh that changes an MSRP or a mod price flows through
automatically.

Both section tables enumerate the **same 28 configs** Python reads from the order
guide at render time. New configs added to `Data_Trims` later surface on the next
fresh render (consistent with the `Target_Build` seeding story).

---

## Formulas per cell type

Structured references throughout. `[@Col]` is the current-row reference inside the
table that owns the column. Every lookup that could miss is wrapped in `IFERROR`.

### Standard-on check (the comma-string membership test)

`Data_Features.Standard_On` is a **comma-space-joined string** (e.g.
`Willys, Rubicon, Rubicon X`), built by `features.py` with `", ".join(...)`. A
naive `SEARCH("Sport", ...)` would false-positive on `Sport S`, so the test is
**delimiter-bracketed**: wrap the haystack in leading `", "` and trailing `","`,
and search for the trim bracketed the same way.

```
Standard_On_Trim  (TrimPathDetail, TRUE/FALSE) =
  IFERROR(
    ISNUMBER(SEARCH(
      ", " & [@Trim] & ",",
      ", " & INDEX(Features[Standard_On], MATCH([@Feature], Features[Feature], 0)) & ","
    )),
    FALSE)
```

Worked check of the delimiter safety: for a feature standard on `Willys, Rubicon,
Rubicon X`, the haystack becomes `", Willys, Rubicon, Rubicon X,"`. Trim `Rubicon`
→ needle `", Rubicon,"` → found. Trim `Rubicon X` → needle `", Rubicon X,"` →
found. Trim `Sport` → needle `", Sport,"` → **not** found (no false match inside
`Rubicon`/`Rubicon X`). A feature standard on `Sport, Sport S` → haystack
`", Sport, Sport S,"`; needle `", Sport,"` matches the first element, `", Sport S,"`
matches the second — both resolve correctly. `SEARCH` is case-insensitive and
treats no trim-name character as a wildcard, so the match is exact-token.

### Included gate

```
Included  (TrimPathDetail, "Yes"/"No") =
  IFERROR(INDEX(Target_Build[Include], MATCH([@Feature], Target_Build[Feature], 0)), "No")
```

### Aftermarket parts cost (join Data_ModPricing by Feature name)

```
Aftermarket_Parts  (TrimPathDetail) =
  IFERROR(INDEX(ModPricing[Parts_Cost], MATCH([@Feature], ModPricing[Feature], 0)), "")
```

### Aftermarket labor cost (install hours × labor-rate named range)

```
Aftermarket_Labor  (TrimPathDetail) =
  IFERROR(INDEX(ModPricing[Install_Hours], MATCH([@Feature], ModPricing[Feature], 0)) * Input_Labor_Rate, "")

Aftermarket_Total  (TrimPathDetail) =
  IFERROR([@Aftermarket_Parts] + [@Aftermarket_Labor], "")
```

### Factory option price (MVP: N/A pending Data_Options)

Per-trim factory-option pricing lives in `Data_Options`, which is **not populated
in MVP** (`Data_Features.Factory_Option_Price` is null by design — a single scalar
per feature can't express per-trim option pricing, e.g. the Steel Bumper Group is
$1,495 only on Rubicon and unavailable elsewhere). Recommendation **(a)**: treat
factory-option paths as explicitly unavailable in MVP rather than stubbing a fake
number.

```
Factory_Option_Price  (TrimPathDetail)  = "N/A (pending Data_Options)"   [literal text]
```

The `Factory_Options_Cost` column in the summary is likewise the literal
`"N/A (pending Data_Options)"` and is **excluded from `Landed_Cost`**. The landed
figure is therefore "MSRP + aftermarket-to-target," which is the honest MVP
number: it slightly *over*-states cost for any feature a trim could have taken as a
cheaper factory option (e.g. Rubicon's steel bumper at $1,495 factory vs $1,300 +
labor aftermarket), and the doc's data-notes flag this so a later IC wiring
`Data_Options` can add the min(factory, aftermarket) path.

### Per-feature contribution (0 if not included, 0 if standard, else aftermarket)

Split into parts / labor so the summary can show the two categories separately
(spec's decomposition), then sum:

```
Parts_Applied  (TrimPathDetail) =
  IF([@Included] <> "Yes", 0, IF([@Standard_On_Trim], 0, IFERROR([@Aftermarket_Parts], 0)))

Labor_Applied  (TrimPathDetail) =
  IF([@Included] <> "Yes", 0, IF([@Standard_On_Trim], 0, IFERROR([@Aftermarket_Labor], 0)))

Contribution_to_Landed  (TrimPathDetail) =
  [@Parts_Applied] + [@Labor_Applied]
```

`Standard_On_Trim` returns a real boolean, so `IF([@Standard_On_Trim], …)` needs no
comparison operator.

### Summary: base MSRP (keyed join, not positional)

```
Base_MSRP  (TrimPathSummary) =
  SUMIFS(Trims[MSRP], Trims[Trim], [@Trim], Trims[Body], [@Body], Trims[Powertrain], [@Powertrain])
```

`Trim` + `Body` + `Powertrain` uniquely identify each of the 28 configs, so
`SUMIFS` returns that config's single MSRP. Keyed rather than positional so it is
robust to any row reordering in `Trims`, and it survives refresh (which rewrites
`Trims[MSRP]` in place). *(Alternative: `INDEX(Trims[MSRP], MATCH(1,
(Trims[Trim]=[@Trim])*(Trims[Body]=[@Body])*(Trims[Powertrain]=[@Powertrain]), 0))`
as a CSE/array formula — same result, but `SUMIFS` avoids array entry, so prefer
it.)*

### Summary: aftermarket costs (SUMIFS over the detail table)

```
Aftermarket_Cost  (TrimPathSummary, parts) =
  SUMIFS(TrimPathDetail[Parts_Applied], TrimPathDetail[Config_Key], [@Config_Key])

Aftermarket_Labor_Cost  (TrimPathSummary, labor) =
  SUMIFS(TrimPathDetail[Labor_Applied], TrimPathDetail[Config_Key], [@Config_Key])
```

### Summary: landed cost and delta

```
Landed_Cost  (TrimPathSummary) =
  [@Base_MSRP] + [@Aftermarket_Cost] + [@Aftermarket_Labor_Cost]

Delta_vs_Cheapest  (TrimPathSummary) =
  [@Landed_Cost] - MIN(TrimPathSummary[Landed_Cost])
```

`MIN(TrimPathSummary[Landed_Cost])` is a structured self-reference over the column
— the cheapest of all 28 landed paths — so the delta needs no hardcoded range. The
cheapest overall will typically be a 2-door Sport (lowest MSRP); the delta is a
global reference point, while the head-to-head the user cares about (Sport-mods vs
at-target Rubicon within one body/powertrain) is read directly off two
`Landed_Cost` cells.

---

## Worked example — community-anchored calibration

**Target build (5 features marked `Include = Yes` in `Target_Build`):**

| Target feature | `Data_Features` name | `feature_id` | `standard_on` |
|---|---|---|---|
| Rear locker | Rear Locker | `rear_locker` | Willys, Rubicon, Rubicon X |
| 35" tires | 35-Inch Tires (Factory) | `tires_35_factory` | Rubicon X |
| Rock rails | Rock Rails | `rock_rails` | Willys, Rubicon, Rubicon X |
| Steel front bumper | Steel Front & Rear Bumpers | `steel_bumpers` | *(none)* |
| Winch | Factory Warn Winch | `winch` | *(none)* |

**Aftermarket data from `data/mod_pricing.json` (labor rate = $120/hr):**

| Feature | Parts | Install hrs | Labor = hrs×$120 | Aftermarket total |
|---|---:|---:|---:|---:|
| Rear Locker | $1,200 | 5.0 | $600 | $1,800 |
| 35-Inch Tires (Factory) | $1,700 | 1.5 | $180 | $1,880 |
| Rock Rails | $780 | 2.0 | $240 | $1,020 |
| Steel Front & Rear Bumpers | $1,300 | 3.0 | $360 | $1,660 |
| Factory Warn Winch | $800 | 2.0 | $240 | $1,040 |

**Base MSRPs from `Data_Trims` (JLU 4-door, V6 8AT = QOP prefix 24):**

| Config | QOP | MSRP |
|---|---|---:|
| JLU Sport V6 8AT | 24B | $41,490 |
| JLU Willys V6 8AT | 24W | $49,810 |
| JLU Rubicon V6 8AT | 24R | $53,770 |

### Path 1 — JLU Sport V6 8AT + all mods aftermarket

Sport is the base package; **none** of the five target features are standard on it,
so every one is an aftermarket line (`Standard_On_Trim = FALSE` → `Contribution =
parts + labor`).

| Feature | Standard? | Parts_Applied | Labor_Applied | Contribution |
|---|---|---:|---:|---:|
| Rear Locker | no | $1,200 | $600 | $1,800 |
| 35-Inch Tires | no | $1,700 | $180 | $1,880 |
| Rock Rails | no | $780 | $240 | $1,020 |
| Steel Bumpers | no | $1,300 | $360 | $1,660 |
| Winch | no | $800 | $240 | $1,040 |
| **Aftermarket subtotal** | | **$5,780** | **$1,620** | **$7,400** |

`Landed_Cost` = 41,490 + 5,780 + 1,620 = **$48,890**

### Path 2 — JLU Willys V6 8AT + mods to reach target

Willys ships with **Rear Locker** (DSH E-Locker) and **Rock Rails** (MEF sill
rails) standard → both contribute $0. It still needs 35s, steel bumpers, and a
winch aftermarket.

| Feature | Standard? | Parts_Applied | Labor_Applied | Contribution |
|---|---|---:|---:|---:|
| Rear Locker | **yes (Willys)** | $0 | $0 | $0 |
| 35-Inch Tires | no | $1,700 | $180 | $1,880 |
| Rock Rails | **yes (Willys)** | $0 | $0 | $0 |
| Steel Bumpers | no | $1,300 | $360 | $1,660 |
| Winch | no | $800 | $240 | $1,040 |
| **Aftermarket subtotal** | | **$3,800** | **$780** | **$4,580** |

`Landed_Cost` = 49,810 + 3,800 + 780 = **$54,390**

### Path 3 — JLU Rubicon V6 8AT + mods to reach target

Rubicon ships with **Rear Locker** and **Rock Rails** standard. Critically for this
config, 35s are **not** standard (only on Rubicon X) and — because the factory
Xtreme 35 package (`AGB`) requires the 2.0T engine, not the V6 — a V6 8AT Rubicon
has **no factory 35" path at all**; 35s must be aftermarket. Steel bumpers (`AD3`,
$1,495 factory) and the winch (`XE5`, $1,995 factory) are factory *options*, but
those paths are N/A in MVP (no `Data_Options`), so they too show aftermarket.

| Feature | Standard? | Parts_Applied | Labor_Applied | Contribution |
|---|---|---:|---:|---:|
| Rear Locker | **yes (Rubicon)** | $0 | $0 | $0 |
| 35-Inch Tires | no | $1,700 | $180 | $1,880 |
| Rock Rails | **yes (Rubicon)** | $0 | $0 | $0 |
| Steel Bumpers | no *(factory AD3 N/A in MVP)* | $1,300 | $360 | $1,660 |
| Winch | no *(factory XE5 N/A in MVP)* | $800 | $240 | $1,040 |
| **Aftermarket subtotal** | | **$3,800** | **$780** | **$4,580** |

`Landed_Cost` = 53,770 + 3,800 + 780 = **$58,350**

### Calibration check

| Path | Base MSRP | Aftermarket | **Landed** |
|---|---:|---:|---:|
| JLU Sport V6 8AT + all mods | $41,490 | $7,400 | **$48,890** |
| JLU Willys V6 8AT + mods | $49,810 | $4,580 | **$54,390** |
| JLU Rubicon V6 8AT + mods | $53,770 | $4,580 | **$58,350** |

- **Sport-mods vs at-target Rubicon:** 58,350 − 48,890 = **$9,460 cheaper**.
  Squarely inside the community "$8–12k" band.
- **On parts alone** (labor excluded): Sport 41,490+5,780 = 47,270 vs Rubicon
  53,770+3,800 = 57,570 → **$10,300**. Also in-band, satisfying the "cheaper by
  ~$8–12k on parts alone" success criterion.
- Willys sits between, as expected: it pre-includes the locker and rails (the two
  features driving the Sport→Willys MSRP jump), so its landed lands ~$4k under
  Rubicon and ~$5.5k over Sport.

**Reality-check / transparency framing.** The tool reports Sport-mods as ~$9.5k
cheaper *on price*, and that is the whole point of the layer — but it does **not**
call Sport the winner. The costs it does **not** blend into this number, and which
live as flags in other layers, are exactly what a Wrangler buyer weighs against
that $9.5k:

- **Driveline-mod warranty exposure** — the rear locker and (in a realistic 35s
  build) a regear are driveline modifications. Magnuson-Moss protects against
  blanket denial, but claims tied to the modified components are the owner's risk.
  Captured in the warranty layer (spec class #14 / risk register #18), not here.
- **Resale** — a factory Rubicon typically holds value better than a modded Sport;
  the market prices the badge and the un-cut warranty. Captured in the
  exit-value/depreciation layer (anti-double-count rule: resale is an exit-value
  effect, not a repair line).
- **Time-to-build & downtime** — the Sport path is ~13.5 aftermarket install
  hours plus parts sourcing and shop scheduling; the Rubicon is closer to
  turn-key. Captured qualitatively, not monetized into landed cost.

None of these are rolled into a composite score (spec: "Rejected: weighted
composite risk scores"). The user sees the $9.5k price gap and the trade-offs side
by side and picks.

**Secondary scenario (why the tab is a live model, not a fixed table).** A
*realistic* 35" build usually also needs a lift and, on a Sport, a regear. If the
user additionally marks **35-Inch Tire Suspension** (`factory_35_suspension`:
$1,800 + 6h → $2,520) and **4.10 Axle Ratio** (`axle_ratio_410`: $800 + 8h →
$1,760):

- Sport needs **both** (no factory lift, ships with tall highway gears) → +$4,280 →
  **$53,170**.
- Willys and Rubicon already have the 4.10 axle standard and need only the lift →
  +$2,520 → Willys **$56,910**, Rubicon **$60,870**.
- Sport-vs-Rubicon narrows to 60,870 − 53,170 = **$7,700**.

The regear the Sport needs to run 35s honestly *closes* part of the gap — the tool
surfaces that instead of hiding it, and still clears the $5k guard rail. This is
the community-anchored behavior: the answer moves with the inputs, in the
direction experienced builders expect.

---

## Test cases for IC #19 to validate against

E2E assertions (extend `tests/test_e2e.py`). "Landed cost" means the computed
`TrimPathSummary[Landed_Cost]` cell for the config after the target build above is
marked and formulas evaluate. Because openpyxl does not calculate formulas, the
test either (i) recomputes the expected value from the same source data and asserts
the formula *string* is the specified one, or (ii) opens the rendered file through
LibreOffice/`formulas`-lib to force a calc; **recommendation: assert the recomputed
arithmetic against a small Python re-derivation of the five-feature model** (the
numbers below) and separately assert the formula text uses structured references.

1. **Sport landed ≈ worked example.** JLU Sport V6 8AT + the 5-feature target →
   **$48,890**, within **$50** (tolerance absorbs a mod-price refresh).
2. **Rubicon landed ≈ worked example.** JLU Rubicon V6 8AT + target → **$58,350**,
   within **$50**.
3. **Willys landed ≈ worked example.** JLU Willys V6 8AT + target → **$54,390**,
   within **$50**. *(Not required by the prompt; cheap to add and pins the middle
   path.)*
4. **Calibration guard rail.** Sport-mods landed < Rubicon-at-target landed by
   **at least $5,000** (actual $9,460). This is the community-wisdom invariant;
   it must hold even as prices drift.
5. **No hardcoded cell addresses in formulas.** Grep every formula string written
   to `Analysis_TrimPath` for the pattern `\$A\$` (and more generally `\$[A-Z]+\$[0-9]`)
   → **0 hits**. All references are structured (`Trims[...]`, `Features[...]`,
   `ModPricing[...]`, `Target_Build[...]`, `TrimPathDetail[...]`,
   `TrimPathSummary[...]`) or named ranges (`Input_Labor_Rate`).
6. **`Trims_MSRP` still resolves.** The pre-existing `Trims_MSRP` named range
   (`= Trims[MSRP]`) is unaffected by adding this tab — assert it is still defined
   and points at `Trims[MSRP]` after render.
7. **Standard-on delimiter safety.** Assert `Sport` is *not* counted standard for a
   feature whose `Standard_On` is `Sport S, Willys, Rubicon, Rubicon X` (guards the
   `Sport`-in-`Sport S` false-positive the bracketed `SEARCH` prevents). E.g.
   Enhanced Adaptive Cruise (`adaptive_cruise`) is standard on `Sport S`+ but the
   base `Sport` path must treat it as not-standard.
8. **Two Analysis tables exist.** `Analysis_TrimPath` carries Excel Tables
   `TrimPathSummary` (28 data rows) and `TrimPathDetail` (28 × 20 = 560 data rows).
9. **Refresh preserves selections.** After marking `Target_Build` includes and
   running `engine refresh`, the `Include` values are unchanged (extends the
   existing `test_refresh_preserves_user_edits` spirit to the new section).

---

## Implementation notes for IC #19

Files IC #19 will touch (all code changes are IC #19's; this IC touches none):

- **`src/engine/workbook.py`**
  - Append `("Labor rate ($/hr)", "Input_Labor_Rate")` to `INPUT_ROWS`, and write
    the default value `120` into that value cell in `_render_inputs` (the label
    loop writes column A; add a matching column-B default write for this row, or a
    small `INPUT_DEFAULTS` map). `_add_named_ranges()` already exposes it — no
    change there.
  - Render the `Target_Build` section on `Inputs` below the single-cell block:
    header + wrapped subheader + a `Target_Build` Excel Table (`Feature`,
    `Include`) seeded from mod-pricing coverage with `Include="No"`; attach a
    `Yes,No` data-validation dropdown to the `Include` column. Reuse
    `xlsx.write_data_table`? It appends `Source`/`As_Of_Date` provenance columns,
    which are wrong for a user-input table — so add a **thin table helper** (or a
    `provenance=False` flag on `write_data_table`) that lays a plain two-column
    Excel Table without provenance. This is the one place a new `xlsx.py` helper is
    justified; see below.

- **`src/engine/xlsx.py`** *(small, optional but recommended)*
  - `write_data_table` hardcodes `PROVENANCE_COLUMNS` onto every table. `Inputs`'s
    `Target_Build` is a user table with no provenance, and the two `Analysis_*`
    tables hold formulas, not provenance-carrying data. Add a helper for
    "table-without-provenance" (either a `include_provenance: bool = True` param on
    `write_data_table`, or a sibling `write_plain_table`). Openpyxl writes the
    formula strings fine on its own, so no formula-writing helper is needed — the
    only discipline worth centralizing is *table creation* so the structured-ref
    guarantee is uniform. Keep it minimal.

- **`src/engine/analysis/trim_path.py`**
  - Replace the title-only `setup_formulas(ws)` with the two-section build:
    1. Read the 28 configs from `engine.data.trims.load()` (or re-read the order
       guide) to enumerate `Trim`/`Body`/`Powertrain` literals for both tables.
    2. Read the 20 covered feature display names from
       `engine.data.mod_pricing` (reuse its id→name map) to enumerate the detail
       table's feature axis and to seed `Target_Build`.
    3. Write `TrimPathDetail` (560 rows) with the per-column formulas above, wrap
       it in an Excel Table named `TrimPathDetail`.
    4. Write `TrimPathSummary` (28 rows) with its formulas, wrap it in
       `TrimPathSummary`.
  - Formulas are written as plain strings via `ws.cell(...).value = "=..."`;
    openpyxl preserves them. Number-format the dollar columns for legibility.

- **Tests** — extend `tests/test_analysis_modules.py` (formula-string assertions
  on a blank sheet) and `tests/test_e2e.py` (the content/calibration assertions
  in the section above). `pytest` stays green with no skips.

Nothing in `data/`, `spec.md`, `README.md`, or `workflow.md` changes.

---

## Data issues noted for a follow-on IC (do NOT fix in IC #19)

Found while grounding the worked example; flagged here per the IC's
"note-don't-fix" rule.

1. **`ModPricing` is body-agnostic.** Parts costs are 4-door-typical, but several
   parts are cheaper on the 2-door (e.g. `mod_pricing.json` notes Rugged Ridge XHD
   sliders are $779.99 for 4-door vs $599.99 for 2-door; 35" tire sets differ too).
   The single `Parts_Cost` per feature slightly over-states 2-door landed costs.
   The worked example (all 4-door) is unaffected. A future IC could add a
   body-style dimension to `Data_ModPricing`.

2. **Factory-option paths are invisible until `Data_Options` is wired.** MVP landed
   costs use aftermarket for features a trim could take as a *cheaper* factory
   option (Rubicon steel bumper $1,495 factory vs $1,660 aftermarket-w/labor;
   winch $1,995 factory). Landed is therefore a mild over-estimate on option-heavy
   trims. When `Data_Options` lands, the contribution should become
   `MIN(factory_option, aftermarket)` per trim, and the summary's
   `Factory_Options_Cost` column should carry the chosen factory dollars. Flagged,
   not fixed.

3. **`winch` prerequisite is not enforced in the model.** A factory winch requires
   a steel front bumper, and the aftermarket winch notes say the same. When both
   are in the target build (as here) the math is right, but marking `winch` without
   `steel_bumpers` would under-count (no bumper to mount it). A later IC could add a
   prerequisite check/flag. Not a blocker for MVP transparency.

## Spec commitments touched

None. This design implements spec "Report shape" §3 (trim-path three-price
transparency + landed-cost comparison) as written, honors the Excel-Tables /
named-range discipline ("Implementation architecture"), and the transparency / no-
false-precision / community-anchored-calibration principles ("Design principles").
The `Input_Labor_Rate` named range operationalizes the class #13 "install labor =
shop quote (not public)" gap by making the rate a single user input rather than a
baked-in guess, consistent with `mod_pricing.json`'s stated design. No spec change
is required; if the strategic hub later wants factory-option paths in MVP, that is a
`Data_Options` scope decision, not a change to this tab's design.
