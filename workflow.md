# Workflow — Delegated Prompts

Execution instructions for spawning tactical sub-contexts. This file is prompts only. See `spec.md` for goals, framework, locked decisions, and taxonomy.

## How to use

1. Pick a prompt whose **Spawn when** criteria are met
2. Invoke via the `Agent` tool with the recommended `subagent_type`, or paste into a fresh Claude Code session
3. Sub-context writes its output to the specified path
4. Return to the strategic hub to review before spawning downstream work

## Git model for delegated contexts

Each workstream runs on its own branch. The sub-context:
- Creates and works on a branch named after the task slug (e.g., `discovery-pass`, `parse-order-guides`)
- Commits its work as it goes — small, self-contained commits with clear messages
- Does **NOT** push to `origin`
- Does **NOT** merge to `main` and does **NOT** delete branches
- Returns the branch name in its final message so the strategic hub can review and integrate

The strategic hub reviews the branch, merges to `main` (squash for cleaner history), pushes, and deletes the branch.

For parallel spawns of independent workstreams, use `isolation: "worktree"` on the `Agent` tool invocation so each agent gets its own checkout on its own branch — avoids filesystem and git-state collisions. Sequential spawns don't need this.

---

## #5 — Discovery pass (variable taxonomy + source validation)

- **Spawn when:** any time (independent of strategic locks)
- **Agent type:** `general-purpose`
- **Output:** `discovery/report.md`
- **Escalation:** returns for review before any modeling begins

**Prompt:**

```
You are running a discovery pass for a 2026 Jeep Wrangler purchase decision engine.

Read C:\claude\Wrangler\spec.md in full for context before starting. Pay particular attention to the "Variable taxonomy" section and "Design principles."

Goal: Validate and refine the variable taxonomy, then identify concrete data sources per variable class. Do NOT collect data yet — this is source discovery and validation only.

Deliverables (write to C:\claude\Wrangler\discovery\report.md):

1. Refined variable taxonomy. Take the draft in spec.md. Add missing variables, correct misplaced ones, flag ones you're unsure about. Wrangler-specific variables that don't appear in a generic car-buying framework are especially valuable to surface.

2. Source candidates per variable class. For each class, name concrete sources with:
   - URL / access path
   - What specific fields they provide (not "pricing info" — list actual data points)
   - Access mechanism (public web, API, requires login, requires paid subscription, industry-only)
   - Refresh frequency they support
   - Quality/reliability assessment
   - Known biases or gaps

   Minimum sources to evaluate: Edmunds (TMV, True Cost to Own, private-party/dealer values, Ask-a-Dealer forum threads for MF+residuals), CarsDirect Deals, KBB, iSeeCars, CarGurus, Jeep.com incentive lookup, JLWranglerForums, WranglerForum, Reddit r/JeepWrangler, Northridge4x4 / Quadratec (mod parts pricing), IRS §30D guidance (4xe tax credit), state DOR pages (sales tax + out-of-state title mechanics).

3. Community landscape check. What forums, subreddits, YouTube channels, Instagram accounts are the active 2026 Wrangler community using? What variables does the community argue about that might not appear in a generic taxonomy?

4. Unknown unknowns. What did you look for that wasn't publicly answerable? What questions require direct contact (dealer quotes, insurance quotes, PPI shops, state DMV calls)?

5. Recommended collection cadence per source (weekly / monthly / one-time / on-demand).

Scope boundaries:
- Do NOT collect actual data — just discover and validate sources
- Do NOT recommend a purchase, trim, or configuration
- Treat target build spec as a parameter you don't need to know
- Treat 4xe as in-scope for source discovery even if it may later be excluded from the model

Report format: comprehensive but well-organized. Use tables. Flag confidence levels on source claims.

When done, stop. Do not proceed to modeling or data collection.

Git:
- Work on branch `discovery-pass` (create it: `git checkout -b discovery-pass`)
- Commit as you go with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message
```

---

## #6 — Parse order guide PDFs

- **Spawn when:** any time (independent of strategic locks)
- **Agent type:** `general-purpose`
- **Output:** `config/order_guide.json` + `config/order_guide_notes.md`
- **Escalation:** returns for schema review before use in modeling

**Prompt:**

```
Parse the two 2026 Jeep Wrangler order guide PDFs in C:\claude\Wrangler\Ordering_Sheets\ into a structured JSON file at C:\claude\Wrangler\config\order_guide.json.

Read C:\claude\Wrangler\spec.md sections on "Provenance framework" and "Multi-axis scenario framework" first — the JSON schema must support scenario-builder use and provenance stamping.

The two PDFs:
- 2026-jeep-wrangler-JL-2-door-orderguide-pricelist.pdf
- 2026-jeep-wrangler-JLU-4-door-orderguide-pricelist.pdf

Extract per body style:
- All trims with base MSRP and (if available) invoice
- All package options with contents (what each package bundles) and pricing
- All standalone options with pricing
- Powertrain options (V6, 2.0T, 4xe if applicable) with pricing deltas
- Wheel and tire options
- Color options with pricing deltas
- Destination charge / freight
- Package mutual-exclusions and prerequisites (if the PDF states them)
- Anything the PDF flags as "required with" or "not available with"

JSON schema goals:
- Structured so a scenario builder can programmatically construct a config (pick trim + packages + options) and compute MSRP
- Each field carries provenance: `source: "order_guide_2026"` and `as_of_date: "<PDF publication date if visible, else null>"`
- Missing/uncertain fields explicitly `null` with a `notes` field explaining why
- Package contents should be enumerable (list of items included) for later mod-adjusted cost analysis

Deliverables:
1. C:\claude\Wrangler\config\order_guide.json — the structured data
2. C:\claude\Wrangler\config\order_guide_notes.md — anything you couldn't parse cleanly, ambiguities, page references for verification

Scope boundaries:
- Do NOT include invoice-calculation approximations if the PDF doesn't state invoice — flag as unknown
- Do NOT extrapolate or infer content not in the PDFs
- Do NOT design the scenario builder or engine — just structure the source data

When done, stop. Return the two files for review.

Git:
- Work on branch `parse-order-guides` (create it: `git checkout -b parse-order-guides`)
- Commit as you go with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message
```

---

## #11 — Prior art investigation

- **Spawn when:** any time (independent of strategic locks)
- **Agent type:** `general-purpose`
- **Branch:** `prior-art-survey`
- **Output:** `prior-art/report.md`
- **Escalation:** returns for review; result may collapse the "build" plan or leave it intact

**Prompt:**

```
You are running a focused investigation for the 2026 Jeep Wrangler decision engine project.

Read C:\claude\Wrangler\spec.md in full for context before starting. It defines what we're building.

Goal: Answer one specific question — does any existing product, tool, framework, or service materially displace ≥50% of the engine's function as defined by spec.md? This is a focused investigation, NOT a landscape scan of car-buying tools.

The engine's differentiating scope (things any prior art must match to displace us):
- Multi-axis scenario ranking (vehicle condition × trim/config × sourcing channel × financing method × timing)
- Mod-adjusted target-build value math (target-build parameter that adjusts trim value based on what you'd otherwise install)
- National-delivery discount-dealer scenarios (Mark Dodge / Granger style) as a first-class sourcing option
- Provenance-tracked values (every value carries source + as_of_date)
- Re-runnable as market conditions change (not a one-shot advisory)
- Wrangler-specific (not generic auto)
- Personal / customizable inputs (budget, credit, state, use case, target build)

Deliverables (write to C:\claude\Wrangler\prior-art\report.md):

1. Strongest 2-3 candidates evaluated in depth. For each:
   - What it is, access model (free / paid / service), extensibility
   - Which of the differentiating dimensions above it addresses, and how well
   - Which it does NOT address
   - Whether it's re-runnable or one-shot
   - Whether provenance is exposed

2. Named recommendation: build / adopt-in-part / adapt-existing / build-only-for-gap. Justify.

3. Optional: any specific features, data structures, or design ideas from the candidates worth adopting even if we build our own engine.

Candidates worth prioritizing evaluation on:
- CarEdge (especially the paid subscription tier and coaching tools — check what's actually behind the paywall)
- Vincentric consumer tools (if any exist beyond B2B ALG-style products)
- Open-source projects on GitHub (search: "car TCO calculator", "vehicle purchase decision", "lease vs buy engine", "auto tco")
- Wrangler-community-built tools (spreadsheets shared on JLWranglerForums, GitHub repos, etc.)
- Any other candidate you discover along the way

Scope boundaries:
- Do NOT catalog data sources (discovery pass #5 already covered that — see discovery/report.md)
- Do NOT evaluate every car-buying tool — only ones that would displace the engine as a whole
- Do NOT build anything — this is a research task
- Time cap: ~3–5 hours

Report length: target ≤1500 words. Prioritize decisiveness over comprehensiveness.

When done, stop.

Git:
- Work on branch `prior-art-survey` (create it: `git checkout -b prior-art-survey`)
- Commit as you go with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message
```

---

## #12 — Used-4xe risk penalty modeling investigation

- **Spawn when:** any time (independent of strategic locks)
- **Agent type:** `general-purpose`
- **Branch:** `4xe-risk-model`
- **Output:** `4xe-risk/proposal.md`
- **Escalation:** returns as a design proposal for #8 (TCO framework) to consume; not an execution

**Prompt:**

```
You are running a focused investigation for the 2026 Jeep Wrangler decision engine project.

Read C:\claude\Wrangler\spec.md in full for context. Pay particular attention to:
- "Risk modeling approach" section — the three-layer framework we've committed to
- "Findings shaping the engine" section — especially finding #1 (§30D/§25E/§45W repeal) and finding #4 (recall risk register)
- "Used case — Tier 2" section — defines the sole 4xe scenario in scope: Used 2023 Rubicon 4xe 4dr ~20k mi
- Classes #18 (recall risk register) and #19 (powertrain profile) in the taxonomy

Also read C:\claude\Wrangler\discovery\report.md sections on 4xe (executive summary finding #1, §2.7 recall/defect risk register, §3.2 community findings on 4xe).

Goal: Design the risk-penalty model for the used-4xe scenario. Concretely, produce a proposal for HOW the engine mechanically penalizes used-4xe in the TCO/scorecard output.

The framework is committed (Option E per spec's "Risk modeling approach"):
- Quantified TCO line items where risk can be honestly monetized
- Confidence-interval widening for stochastic tail risk
- Qualitative risk-score column for risks that refuse to monetize honestly
- Weighted composite risk scores are REJECTED (false precision)

Your job: fill in the substance. What specific data to source, what math to apply, what appears in the report — for the used-4xe scenario specifically.

Key risk factors to model:
- HV battery health uncertainty on a used unit — degradation profile, replacement cost, service life distribution
- Fire recall applicability + class action drift — which used-4xe MY/VIN ranges are affected, remedy status, park-outside advisories, class action expected value
- Resale trajectory post-§30D repeal — how much has 4xe used resale shifted since the credit repeal, forecast for the next N years
- No §25E used federal credit — expired same act; means no $4k on used
- CARB-state battery-warranty extension — where applicable, extends the 8yr/100k federal floor
- Sourcing PPI-equivalent for battery health — is there a diagnostic beyond a generic PPI that assesses HV battery state? Cost / availability

Deliverables (write to C:\claude\Wrangler\4xe-risk\proposal.md):

1. Data-sourcing plan. For each risk factor above:
   - What specific data point is needed
   - Best source(s)
   - Access mechanism, refresh cadence, confidence
   - Whether it's monetizable or belongs in the qualitative column

2. Monetized risk line items. For each risk that resolves to a TCO line item: the formula (probability × cost), how to calibrate probability, what the expected value range is (with confidence interval).

3. Interval-widening logic. Which specific uncertainties translate to widened intervals on the used-4xe scenario, and by how much.

4. Qualitative risk column entries. Which risks show up as scorecard flags rather than TCO adjustments, and how they're phrased.

5. Sensitivity flags. Which inputs would materially change the used-4xe ranking if they moved by X%.

6. Implementation sketch. Enough for the eventual #8 (TCO framework build) context to consume — data-file schema, function signatures, or however you'd frame the interface.

Scope boundaries:
- Do NOT model new-4xe risk (new 4xe is out of scope per spec)
- Do NOT collect the actual data yet — this is a design proposal, not an execution
- Do NOT design the full engine — just the used-4xe risk module
- Follow "no false precision" — where you don't have real calibration data, flag it as an assumption to be validated, not a made-up number

Report length: target ≤2000 words. Include tables where they help.

When done, stop.

Git:
- Work on branch `4xe-risk-model` (create it: `git checkout -b 4xe-risk-model`)
- Commit as you go with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message
```

---

## #14 — Scaffolding: walking skeleton with passing tests

- **Spawn when:** any time (foundational — all subsequent code ICs depend on it)
- **Agent type:** `general-purpose`
- **Branch:** `scaffolding`
- **Isolation:** `worktree` (default for all delegated spawns going forward)
- **Output:** working Python package + minimal .xlsx + green pytest suite
- **Escalation:** returns for review before any real-data or formula IC spawns

**Prompt:**

```
You are running the scaffolding workstream for the Wrangler decision engine project.

Read C:\claude\Wrangler\spec.md in full, particularly the "Implementation architecture" section, "Design principles" (especially "Transparency over recommendation" and "MVP over exhaustive"), and the "Report shape" section. Also read C:\claude\Wrangler\workflow.md's "Git model for delegated contexts" section.

Goal: Build a walking skeleton for the system — hello-world bare-bones end-to-end implementation with a passing pytest suite, so subsequent ICs can plug in one module at a time and always leave the repo in a working state. TDD discipline: every module has a unit test; there is an E2E smoke test that validates the whole pipeline before any real data or formulas exist.

Deliverables (all committed on branch `scaffolding`):

1. Python package structure
   - pyproject.toml using uv-compatible layout (uv is preferred; pip fallback is fine)
   - src/engine/ package layout with __init__.py and CLI entry point
   - tests/ directory with pytest configuration
   - Runtime dependencies: openpyxl, pyyaml, click (or argparse if you prefer)
   - Dev dependencies: pytest, ruff (linting nice-to-have)

2. CLI stubs
   - `engine render` — produces a working (if minimal) .xlsx at a designated output path
   - `engine refresh` — reads an existing .xlsx and (initially) rewrites Data_* tabs in a no-op that preserves the file structure
   - Both commands exit 0 on success and print clear errors on failure

3. Excel skeleton (produced by `engine render`)
   - All tabs exist per spec.md's tab structure:
     User-owned: Inputs, Notes
     Python-owned Data: Data_Trims, Data_Options, Data_Features, Data_Incentives, Data_Lease, Data_ModPricing, Data_Used, Data_TaxRules, Data_Depreciation
     Excel-computed Analysis: Analysis_Levers, Analysis_TrimPath, Analysis_Sourcing, Analysis_Financing, Analysis_Timing, Analysis_OngoingCosts, Analysis_Sensitivity
     Reference: Ref_Provenance, Ref_Legend
   - Every Data_* tab has an Excel Table with headers + one placeholder row (empty). Future ICs extend by row, not by table.
   - Ref_Legend contains a brief explanation of the tab structure + ownership model
   - Named ranges: demonstrate the pattern with at least one named range referencing a table (even if trivial)
   - No real data, no real formulas — that's for later ICs

4. Module stubs (plug-in points for future ICs)
   - src/engine/data/ — one Python file per Data_* tab (e.g., trims.py, options.py, features.py, incentives.py, lease.py, mod_pricing.py, used.py, tax_rules.py, depreciation.py). Each exports load() and render() functions (stubs).
   - src/engine/analysis/ — one file per Analysis_* tab (e.g., trim_path.py, sourcing.py, financing.py, timing.py, ongoing_costs.py, sensitivity.py, levers.py). Each exports setup_formulas() (stub) — formulas are Excel-native but the code sets them up.
   - src/engine/refresh/ — refresh merge logic (stub)
   - src/engine/cli.py — the CLI entry point wiring render + refresh commands

5. Tests (pytest)
   - Unit test per module stub: import the module + trivial assertion establishing the plug-in pattern
   - E2E smoke test: run `engine render` → verify the .xlsx exists → open it with openpyxl → verify every expected tab exists → verify every Data_* tab has an Excel Table set up → verify at least one named range exists
   - E2E refresh-preservation test: run `engine render`, modify a cell on the Inputs tab, run `engine refresh`, verify the Inputs cell edit is preserved
   - All tests pass via `pytest`

6. Documentation
   - README.md at repo root explaining:
     - Architecture (Python renders + refreshes; Excel formulas compute)
     - How to install (uv sync / pip install -e .)
     - How to run render / refresh / tests
     - Plug-in pattern for future ICs (which files to edit, which tests to add, which E2E assertions to extend)
   - No CONTRIBUTING.md needed — the pattern lives in the code + README

Success criteria (all must be true before commit):
- `pytest` passes green with no skips
- `engine render` produces a valid .xlsx that opens cleanly in Excel or LibreOffice
- The .xlsx has all tabs and Excel Table structures per spec
- All module stubs exist so future ICs know where to plug in
- README documents the plug-in pattern

Scope boundaries:
- Do NOT put real data in the .xlsx — empty tables with headers only
- Do NOT write real formulas in Analysis_* tabs — leave them empty for future ICs
- Do NOT touch config/order_guide.json — it's the source of truth for IC #1
- Do NOT add complexity beyond the walking skeleton — every line of code justified by an existing or planned IC that needs it

Git:
- Work on branch `scaffolding` (create it: `git checkout -b scaffolding`)
- Commit incrementally with clear messages (e.g., "scaffold Python package", "add openpyxl render stub", "add E2E smoke test")
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: substantial — foundational work. Take the time to get the plug-in pattern right; subsequent ICs will depend on the discipline this one establishes.
```

---

## #15 — IC #1: real Data_Trims render from config/order_guide.json

- **Spawn when:** any time (scaffolding IC #14 is merged; this is the next step in the vertical slice)
- **Agent type:** `general-purpose`
- **Branch:** `data-trims-real`
- **Isolation:** `worktree`
- **Output:** `src/engine/data/trims.py` real `load()` + extended E2E assertions; all tests green

**Prompt:**

```
You are running IC #1 of the vertical-slice sequence for the Wrangler decision engine. Scaffolding (IC #14) landed the walking skeleton; your job is to replace the Data_Trims stub with real data from the parsed order guide.

Read C:\claude\Wrangler\spec.md "Implementation architecture" section, C:\claude\Wrangler\README.md (especially the "Plug-in pattern for future ICs" section), and inspect the existing code:
- src/engine/data/trims.py (the module you'll be filling in)
- src/engine/xlsx.py (understand how the table is written and provenance columns are handled)
- tests/test_e2e.py (this is where you extend the pipeline validation)
- tests/test_data_modules.py (parametrized tests that will start asserting real rows)

Source data: C:\claude\Wrangler\config\order_guide.json — parsed by an earlier IC (see config/order_guide_notes.md if you need context). Structure: body_styles → JL_2_door / JLU_4_door → trims[] → configurations[]. Each configuration is a fully-delivered price (base + engine/trans + quick order package, before destination). Invoice is null everywhere by design — the guides don't publish it.

Goal: implement Data_Trims for real, so a rendered .xlsx has one row per (trim × body-style × configuration) with actual MSRP values, sourced and dated.

Deliverables (committed on branch data-trims-real):

1. Replace load() in src/engine/data/trims.py with real code
   - Read config/order_guide.json
   - Iterate body_styles → trims → configurations
   - Emit one row per configuration matching COLUMNS = ["Trim", "Body", "Powertrain", "MSRP", "Invoice"]
   - Provenance: Each row should carry Source and As_Of_Date at the end (append to the row). Source = "order_guide_2026" (or read from the JSON's provenance nodes if you prefer); As_Of_Date = "2025-08-06" (the reissue date recorded in the JSON's provenance).
   - Establish and document the row-shape pattern for future data modules to follow (comment or docstring update on the module) — modules return rows that INCLUDE provenance values as the last two elements, matching the header PROVENANCE_COLUMNS xlsx.py appends. Update the module docstring to be crisp about this so IC #2 through #N don't guess.

2. Powertrain field naming: use a human-readable label per configuration. Suggested pattern: "V6 6MT" for the 23-prefix, "2.0T 8AT" for 22-prefix, "V6 8AT" for 24-prefix. If you want to preserve the code prefix as an additional column, propose it — but don't add without justification.

3. Extend tests/test_e2e.py with content assertions
   - Data_Trims row count matches expected (should be ~20+ configurations across both bodies)
   - Spot-check a known value: e.g., JL 2-door Sport V6 6MT MSRP is $33,785 per the order guide notes
   - Spot-check a JLU 4-door value: e.g., JLU Rubicon V6 6MT MSRP is $49,270
   - Provenance columns are populated (Source = "order_guide_2026", As_Of_Date = "2025-08-06") on every row
   - All 50 existing tests still pass

4. If xlsx.py needs a small tweak to handle real rows cleanly (e.g., if the row-length pattern I described above doesn't work with the current placeholder-row logic), fix it — but justify the change in your commit message. The single-owner discipline for xlsx.py means changes there ripple to every data module, so be deliberate.

5. Add a small unit test for the parser (e.g., tests/test_data_trims.py) validating: load() returns > 0 rows; each row has the right shape; provenance is populated.

Success criteria (all must be true before commit):
- `pytest` passes green (existing 50 + new)
- `ruff check` passes clean
- `engine render` produces a valid .xlsx; opening Data_Trims tab visually shows real rows
- README's plug-in pattern section is updated if you changed the pattern

Scope boundaries:
- Do NOT touch Data_Options, Data_Features, or any other Data_* module — that's for later ICs
- Do NOT add real formulas to Analysis_* tabs — separate IC
- Do NOT rewrite xlsx.py unless necessary; small justified tweaks are fine

Git:
- Work on branch `data-trims-real` (create it: `git checkout -b data-trims-real`)
- Commit incrementally with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: modest — this is a bounded IC. Should complete in a few hours max.
```

---

## #16 — IC #2: feature taxonomy + Data_Features real render

- **Spawn when:** any time (IC #15 Data_Trims is merged; independent of IC #17 aftermarket pricing)
- **Agent type:** `general-purpose`
- **Branch:** `data-features-real`
- **Isolation:** `worktree`
- **Output:** `data/features.json` + real `src/engine/data/features.py` load() + extended E2E assertions; all tests green

**Prompt:**

```
You are running IC #2 of the vertical-slice sequence. Data_Trims (IC #1) is merged; your job is to produce the feature taxonomy that Data_Features holds and that Analysis_TrimPath will later use for three-price transparency (standard-embedded / factory-option / aftermarket).

Read C:\claude\Wrangler\spec.md sections "Multi-axis decision framework", "Report shape" (especially the "Trim path" three-price example), and "Implementation architecture". Read C:\claude\Wrangler\README.md's "Plug-in pattern for future ICs". Also read the existing implementations for the row-shape contract:
- src/engine/data/trims.py (reference for the row-shape pattern established in IC #1)
- src/engine/data/features.py (the stub you're filling in — note the declared COLUMNS)
- src/engine/xlsx.py (understand the header + provenance mechanics)

Source data: C:\claude\Wrangler\config\order_guide.json (parsed order guide) + supplementary context in C:\claude\Wrangler\config\order_guide_notes.md and C:\claude\Wrangler\discovery\report.md (§3.2 lists the features the community actually argues about).

Goal: produce a curated feature taxonomy — one row per meaningful *feature* — with the availability matrix (which trims have it standard, denormalized), and render it into the Data_Features Excel Table. Aftermarket pricing is IC #17's job — leave Aftermarket_Price null; do NOT scrape or fabricate parts prices.

Deliverables (committed on branch data-features-real):

1. `data/features.json` — the canonical taxonomy
   - Structure: a JSON object with a `features` array + a `provenance` node (`source`, `as_of_date`) at the top level.
   - Each feature entry: `id` (stable snake_case slug like `rear_locker`, `electronic_sway_disconnect`, `rock_rails`), `name` (human-readable), `category` (one of a small closed set — you propose: `drivetrain`, `suspension`, `wheels_tires`, `body_armor`, `electrical_lighting`, `top_and_doors`, `interior_tech`, etc.), `standard_on` (list of trim names where this feature comes standard — treat body style as a distinguishing dimension, e.g., "Rubicon (JL 2-door)" vs "Rubicon (JLU 4-door)" when they materially differ), optional `notes` field for anything worth preserving (constraints, powertrain conditionals).
   - Scope guidance: aim for ~30–60 features that (a) differentiate trims meaningfully AND/OR (b) are common Wrangler-buyer mod targets. Focus on off-road capability (lockers, sway disconnect, transfer case, axles, tire size, skids, rock rails, bumpers, winch, lift), body/top options (Sky One-Touch, hard top, dual top), and material electronics (LED headlamps, UConnect, safety group). Do NOT enumerate every trim-line comfort/appearance item.
   - Provenance: `{source: "order_guide_2026 + curator", as_of_date: "2026-07-18"}` or similar. Cite the curator step because taxonomy involves judgment.

2. `src/engine/data/features.py` — real render
   - Update the module docstring to point at data/features.json and describe the taxonomy scope (matches what IC #1 did for trims.py).
   - Implement load() to read data/features.json and emit one row per feature matching COLUMNS. Provenance is per-row (row-shape contract from IC #1) — read source and as_of_date from the JSON provenance node.
   - The scaffolding declared: COLUMNS = ["Feature", "Category", "Standard_On", "Factory_Option_Price", "Aftermarket_Price"]. Row emission:
     - Feature = the `name` field (human-readable)
     - Category = the `category` field
     - Standard_On = comma-separated `standard_on` list (informative denorm; the real per-trim availability lives in the taxonomy JSON for later formula work)
     - Factory_Option_Price = None for IC #2 (per-trim option pricing lives in Data_Options and gets joined in Analysis_TrimPath; this column is a placeholder — you may propose dropping it or renaming to Factory_Option_Available (bool). Justify any schema change in your commit message. If you drop or rename, update the smoke test's expected named ranges if applicable.)
     - Aftermarket_Price = None for IC #2 (IC #17 fills this in)
   - Do NOT modify xlsx.py. Do NOT modify other data modules.

3. Extend tests
   - `tests/test_data_features.py` (new): load() returns > 0 rows; row-shape contract; every feature has an id, name, category from the closed set; every standard_on list references known trim names.
   - Extend `tests/test_e2e.py` with content assertions: Data_Features row count matches len(features.json.features); spot-check known features (e.g., a "Rear Locker" row exists with Rubicon in Standard_On; a "Rock Rails" row exists with Willys and Rubicon in Standard_On). Include a check that the taxonomy IDs are all unique (no dup slugs).

4. Update README's plug-in pattern section if IC #2 has established a new pattern the future ICs should follow (e.g., "some data modules read curated data/*.json rather than parsed source data — see features.py").

Success criteria (all must be true before commit):
- pytest passes green (all 56 baseline + any new tests)
- ruff check passes clean
- engine render produces a valid .xlsx; Data_Features tab has real rows
- data/features.json is well-formed, has 30–60 features, unique IDs, categories from a closed set
- The taxonomy is honestly limited to features that meaningfully differentiate or are common mod targets — no filler

Scope boundaries:
- Do NOT touch Data_Trims, Data_Options, or other Data_* modules
- Do NOT fabricate aftermarket prices (IC #17's job)
- Do NOT design Analysis_TrimPath formulas (IC #18's job)
- Do NOT add every options-page item; be curatorial

Judgment calls:
- If a feature is "in a package but not standard alone" (e.g., disconnecting sway bar via Rubicon package), still list it as standard_on that trim; the package equivalence is intentional in the taxonomy.
- If a feature meaningfully differs by body style (e.g., 4-door-only), split it into two entries or note it in `notes`.
- Xtreme Recon variants: the guide has different content 2-door vs 4-door — handle as best-fit; note ambiguities in `data/features.json` per-feature notes rather than in a doc.

Git:
- Work on branch `data-features-real` (create it: `git checkout -b data-features-real`)
- Commit incrementally with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: substantial — this involves both data curation and code. Prioritize a clean, defensible taxonomy over exhaustive feature coverage.
```

---

## #17 — IC #3: aftermarket mod pricing + Data_ModPricing real render

- **Spawn when:** any time (IC #16 features taxonomy is merged; independent of Analysis_TrimPath work)
- **Agent type:** `general-purpose`
- **Branch:** `data-mod-pricing-real`
- **Isolation:** `worktree`
- **Output:** `data/mod_pricing.json` + real `src/engine/data/mod_pricing.py` load() + extended tests; all tests green

**Prompt:**

```
You are running IC #3 of the vertical-slice sequence. Data_Trims (IC #1) and Data_Features (IC #2) are merged. Your job is to produce aftermarket pricing per mod-target feature so Analysis_TrimPath can later compute the three-price transparency (standard-embedded / factory-option / aftermarket).

Read:
- C:\claude\Wrangler\spec.md sections "Multi-axis decision framework", "Report shape" (the trim-path three-price example), and "Implementation architecture"
- C:\claude\Wrangler\README.md's "Plug-in pattern for future ICs" (curated data/*.json pattern is now documented)
- C:\claude\Wrangler\discovery\report.md §2.5 (live-verified aftermarket retailers with confidence flags)
- C:\claude\Wrangler\data\features.json (source-of-truth for feature IDs; every mod-pricing entry keys off these)
- C:\claude\Wrangler\src\engine\data\features.py (the reference for the curated-data pattern)
- C:\claude\Wrangler\src\engine\data\mod_pricing.py (the stub you're filling in — note COLUMNS = ["Feature", "Parts_Cost", "Install_Hours"])

Source data landscape:
- Quadratec (quadratec.com) — 4xe fitment authority per discovery; per-product itemized pricing
- Northridge4x4 (northridge4x4.com) — per-component kit costing; strongest for suspension/armor
- ExtremeTerrain (extremeterrain.com) — the only source giving install hours + difficulty
- No public API; every retailer is HTML. Do NOT scrape at volume — sample representative products per feature (~2-3 sources per feature is fine).
- Do NOT fetch labor $ — retailers don't publish it, and the module intentionally emits Install_Hours (not labor cost) so Excel can multiply by a user-input labor rate downstream.

Goal: produce a curated data/mod_pricing.json holding aftermarket parts cost + install hours per feature (keyed to features.json IDs), and render it into Data_ModPricing.

Deliverables (committed on branch data-mod-pricing-real):

1. data/mod_pricing.json
   Structure: a JSON object with a `pricing` array + top-level `provenance` node (`source`, `as_of_date`) + a `retailers` map documenting URL and reliability tier.

   Each pricing entry:
   - `feature_id` — MUST match an id in data/features.json (validated by tests)
   - `parts_cost` — integer USD, typical/representative price
   - `install_hours` — number, typical shop hours (from ExtremeTerrain when available; note the assumption otherwise)
   - `parts_cost_range` — optional {low, high} when variance is material (e.g., D30 vs D44 locker spec, budget vs premium lift kits)
   - `retailer_sources` — array of {retailer, product, url} entries used to establish the price
   - `notes` — anything worth preserving: variants, warranty impact flags, install caveats

   Provenance node example: `{source: "aftermarket_retailers + curator", as_of_date: "2026-07-18"}`.

2. src/engine/data/mod_pricing.py
   - Update the module docstring to point at data/mod_pricing.json, document the join model (Data_ModPricing rows join Data_Features by Feature name; Analysis_TrimPath will VLOOKUP/INDEX-MATCH), and note that labor rate comes from Inputs (not from this data).
   - Implement load() to read data/mod_pricing.json and emit one row per pricing entry matching COLUMNS = ["Feature", "Parts_Cost", "Install_Hours"] followed by provenance (Source, As_Of_Date). Look up the feature `name` from features.json using feature_id (join at load-time so the Excel column is the display name).
   - Follow the row-shape contract established in IC #1: provenance is per-row.
   - Do NOT modify xlsx.py or workbook.py.

3. Scope guidance for the taxonomy of pricing
   Cover features that are practical aftermarket mod targets. Skip features that are essentially OEM-only or that no one meaningfully aftermarkets:
   - INCLUDE: rear/front locker (via ARB Air Locker or equivalent), electronic sway disconnect (Currie Antirock / RockJock manual disconnect as functional equivalent), rock rails, skid plates, steel front bumper, winch, 33"/35" tires + wheels, lift kits (mild ~2", larger 3+"), LED headlamps, LED aux lighting bar, half doors / tube doors, hard top variants that are aftermarket-available, snorkels if in features.json
   - CONSIDER: winch bumper combos, storage armor, tow package add-ons (hitch retro)
   - EXCLUDE: features where no practical aftermarket exists (Rock-Trac 4:1 transfer case swap is impractical; Selec-Trac; interior tech like UConnect head units are technically aftermarket but out-of-scope for this project)
   - Expected coverage: ~15-25 pricing entries. Not every feature in features.json gets a row here — features with no practical aftermarket should simply be omitted.

4. Tests
   - tests/test_data_mod_pricing.py (new): well-formedness; every feature_id exists in features.json; parts_cost > 0; install_hours >= 0; row-shape contract; retailer_sources non-empty for every entry
   - tests/test_e2e.py extended: Data_ModPricing row count > 0; every row's Feature name matches a feature in Data_Features; parts_cost + install_hours populated; provenance populated
   - All 65 baseline tests remain green (72+ total after this IC)

5. Notes on judgment
   - Prices in this file are captured on the as_of_date. They are known to be sale/coupon-driven and will drift. This is expected; refresh will re-pull later.
   - Where a feature has multiple aftermarket variants at different quality/price tiers (e.g., budget "3-inch lift" at $600 vs premium at $2,500), use the typical/representative choice AND record the range in `parts_cost_range` with notes.
   - Discovery §2.5 confidence flags: Quadratec HIGH; Northridge4x4 HIGH (per-component costing); ExtremeTerrain HIGH (install hours source); Morris4x4 LOW (Cloudflare-gated). Prefer HIGH sources.

Success criteria (all must be true before commit):
- pytest passes green (65 baseline + new)
- ruff check passes clean
- engine render produces a valid .xlsx; Data_ModPricing tab has real rows
- Every feature_id in mod_pricing.json exists in features.json
- Provenance retailer URLs are real (validated at capture time, may 403 automated fetch — that's fine)

Scope boundaries:
- Do NOT modify data/features.json (that's IC #16's artifact)
- Do NOT modify Data_Features or any other data module
- Do NOT design Analysis_TrimPath formulas (IC #18/#19's job)
- Do NOT add named ranges or modify workbook.py — the labor-rate named range will be added when Analysis_TrimPath needs it
- Do NOT fetch aggressively — sample representative products per feature; ~2-3 sources max

Git:
- Work on branch `data-mod-pricing-real` (create it: `git checkout -b data-mod-pricing-real`)
- Commit incrementally with clear messages
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: substantial — this is data curation with retailer research. Prioritize honest, sourced prices over comprehensive feature coverage.
```

---

## #18 — IC #4: Analysis_TrimPath design doc (formulas as markdown)

- **Spawn when:** any time (IC #17 complete; independent of implementation IC)
- **Agent type:** `general-purpose`
- **Branch:** `analysis-trim-path-design`
- **Isolation:** `worktree`
- **Output:** `analysis-designs/trim_path.md` (design doc only; no code changes); reviewed at hub before IC #19 implements

**Prompt:**

```
You are running IC #4 of the vertical-slice sequence — the first *formula design* IC. Your job is to produce a design document for Analysis_TrimPath: how the tab should be laid out, what Excel formulas compute the three-price transparency, and a worked example proving the math against known ground truth. No code changes yet — that's IC #19.

Read:
- C:\claude\Wrangler\spec.md sections "Multi-axis decision framework", "Report shape" (especially the "Trim path" three-price example under section 3), "Implementation architecture" (tab structure + Excel Tables discipline), and "Design principles" (especially "Transparency over recommendation", "No false precision", and "Community-anchored calibration")
- C:\claude\Wrangler\README.md's plug-in pattern
- C:\claude\Wrangler\data\features.json (feature taxonomy — 38 entries; note that standard_on lists are trim-name-only, not body-style-specific)
- C:\claude\Wrangler\data\mod_pricing.json (20 aftermarket pricing entries keyed to feature_id)
- The rendered .xlsx that engine render produces (or inspect via openpyxl): Data_Trims has 28 configuration rows; Data_Features has 38 rows; Data_ModPricing has 20 rows

Goal: produce a design document at `analysis-designs/trim_path.md` that specifies exactly what Analysis_TrimPath displays and what Excel formulas compute it — such that IC #19 can implement the tab mechanically without further design decisions.

Deliverables (committed on branch analysis-trim-path-design):

1. `analysis-designs/trim_path.md` — the design document. Structure:

   ## Purpose
   One paragraph: what the tab shows and why (per spec's "Report shape" section 3 trim-path).

   ## Target build encoding on Inputs tab
   Propose how the user specifies their target build. Recommended approach: Python renders a target-build section on the Inputs tab with one row per aftermarket-target feature (from mod_pricing.json's coverage), each with a Yes/No or checkbox column the user marks. Specify:
   - Section header + explanatory subheader on the Inputs tab
   - Table structure (Feature Name column + Include? column)
   - How Python populates it on first render (reads mod_pricing.json's covered features; user marks after)
   - Excel Table name (e.g., "Target_Build") so formulas can use structured references
   - What happens on refresh — does Python overwrite the Target_Build section (breaking user selections) or leave it alone? (Rule: leave user selections intact; only add rows for newly-covered features on refresh, don't remove.)

   ## New named ranges required
   List every named range Analysis_TrimPath needs beyond what scaffolding already provides. At minimum: Input_Labor_Rate (user's shop labor $/hr). Note that adding these is a small workbook.py edit IC #19 will make.

   ## Analysis_TrimPath layout
   Concrete row/column mockup showing the tab structure. Recommendation: two sections in one tab.
   - Top: per-trim summary — one row per configuration (from Data_Trims, 28 rows), columns for Base_MSRP, Factory_Options_Cost, Aftermarket_Cost, Aftermarket_Labor_Cost, Landed_Cost, and a Delta_vs_Cheapest column
   - Bottom: per-feature-per-trim breakdown — long format, one row per (configuration × target-build feature), columns showing whether it's Standard on this trim, Factory Option Price (null for MVP since per-trim option pricing lives in Data_Options which we haven't wired yet), Aftermarket Price (parts + labor), Contribution_to_Landed (which category actually applies for this trim)
   Alternative layouts are welcome if you can justify them. Pick one.

   ## Formulas per cell type
   For every column that uses a formula, write the Excel formula as text using structured references (e.g., `INDEX(ModPricing[Parts_Cost], MATCH(...))` — never `A2:A20`). Cover:
   - Standard-on check: is feature X in this trim's standard_on comma-string?
   - Aftermarket parts cost lookup from Data_ModPricing joined by Feature name
   - Aftermarket labor cost = install_hours × Input_Labor_Rate
   - Total aftermarket contribution per feature (0 if standard on this trim; else parts + labor)
   - Landed cost per trim = Base_MSRP + sum of aftermarket contributions for target-build features
   - Delta_vs_Cheapest across trims
   Note explicitly: Data_Features standard_on is comma-joined string; formulas will use ISNUMBER(SEARCH(...)) or similar. Note the exact pattern.
   Note gaps: factory option pricing is null in MVP (Data_Options isn't populated yet). The design should either (a) treat factory-option paths as unavailable in MVP with a clear "N/A pending Data_Options" note, or (b) propose a stub that's obviously placeholder. Recommend (a).

   ## Worked example — community-anchored calibration
   Pick a specific target build:
   - Rear locker + 35" tires + rock rails + steel front bumper + winch
   Show the computed landed cost for these three paths using ACTUAL data from data/features.json + data/mod_pricing.json + Data_Trims:
   - JLU 4-door **Sport** V6 8AT + all mods aftermarket
   - JLU 4-door **Willys** V6 8AT + mods needed to reach target
   - JLU 4-door **Rubicon** V6 8AT + mods needed to reach target
   Enumerate for each: base MSRP, which features are already standard, which mods are needed, parts cost, install hours × assumed labor rate ($120/hr), total landed. Show your math cell by cell.
   Reality-check against community wisdom: Sport-plus-mods should come out numerically cheaper than at-target Rubicon by roughly $8-12k, but the design doc should note the trade-offs (warranty on driveline mods, resale, time to build) that the tool captures in *other* layers (this is critical for the transparency framing).

   ## Test cases for IC #19 to validate against
   List specific assertions the E2E test should check after IC #19 implements this:
   - Landed cost for JLU Sport V6 8AT + target build matches the worked example within $50 (accounting for potential price refresh)
   - Landed cost for JLU Rubicon V6 8AT + target build matches within $50
   - Sport-plus-mods landed < Rubicon-at-target landed by at least $5,000 (calibration guard rail)
   - No formula references hardcoded cell addresses (grep for `\$A\$` — should return 0 hits inside formulas)
   - The Trims_MSRP named range still resolves after the tab is added

   ## Implementation notes for IC #19
   Enumerate any workbook.py / xlsx.py / Data_* changes required by this design. At minimum:
   - Add Input_Labor_Rate named range to Inputs tab (with a sensible default cell value of $120/hr)
   - Render the Target_Build section on Inputs tab (Python side)
   - Modify Analysis_TrimPath setup_formulas() to write the two-section layout with real formulas
   - Consider whether xlsx.py needs a helper for formula-writing (probably not — openpyxl handles it, but flag it if the discipline benefits)

2. Do NOT touch any code. This IC is design only. If you find issues in the data (features.json errors, mod_pricing gaps), NOTE them at the end of the design doc for a follow-on IC to fix — do not fix them here.

3. Do NOT modify workflow.md, spec.md, or README.md. If the design changes any commitment in spec.md, flag it at the end of the design doc; the strategic hub will integrate.

Success criteria (all must be true before commit):
- analysis-designs/trim_path.md exists and is complete per the structure above
- The worked example uses REAL data values from features.json, mod_pricing.json, and (for MSRPs) the parsed order guide reachable via engine render
- Every formula in the doc uses structured references (Trims[MSRP], ModPricing[Parts_Cost], Features[Standard_On], Target_Build[Include]) — no `$A$2:$A$20` patterns
- The Sport-vs-Rubicon calibration comes out roughly right (Sport-plus-mods cheaper by ~$8-12k on parts alone)
- No code files touched; pytest is unchanged; ruff is unchanged

Scope boundaries:
- Design doc ONLY — no code, no data changes
- Do not implement anything — the design is IC #19's execution spec
- Do not propose formula patterns for other Analysis_* tabs (Sourcing, Financing, etc.) — one tab at a time

Git:
- Work on branch `analysis-trim-path-design` (create it: `git checkout -b analysis-trim-path-design`)
- Commit as you go (design doc drafts count as commits)
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: substantial — this is design work that unlocks the vertical slice's proof point. The worked example carrying real numbers is critical; don't rush it.
```

---

## #19 — IC #5: Analysis_TrimPath implementation (vertical-slice proof point)

- **Spawn when:** IC #18 design doc is merged (currently merged)
- **Agent type:** `general-purpose`
- **Branch:** `analysis-trim-path-impl`
- **Isolation:** `worktree`
- **Output:** implemented Analysis_TrimPath with real Excel formulas + extended tests; vertical slice end-to-end proof

**Prompt:**

```
You are running IC #5 — the vertical-slice implementation. IC #4 produced the design doc at `analysis-designs/trim_path.md`. Your job is to execute that design mechanically: no new design decisions, no judgment calls that aren't already resolved in the doc.

Read (in order):
1. C:\claude\Wrangler\analysis-designs\trim_path.md — this is your specification. Every formula, every layout choice, every test assertion is spelled out.
2. C:\claude\Wrangler\spec.md "Implementation architecture" section (tab structure + Excel Tables discipline invariants)
3. C:\claude\Wrangler\README.md's plug-in pattern
4. Current implementations you'll modify:
   - src/engine/workbook.py (adds Input_Labor_Rate named range + Target_Build section on Inputs)
   - src/engine/xlsx.py (add the "table without provenance" helper — the design specifies this is one place a targeted extension is justified)
   - src/engine/analysis/trim_path.py (currently a title-only stub; replace with the two-table Analysis_TrimPath build)
5. Existing tests you'll extend:
   - tests/test_e2e.py (add the 9 assertions from the design doc's "Test cases for IC #19 to validate against" section)
   - tests/test_analysis_modules.py (formula-string assertions on a blank sheet if that's the right home for them)
   - tests/test_data_modules.py (may need small updates if the Target_Build table on Inputs changes what the parametrized checks assume)

Goal: implement the design mechanically so that `engine render` produces an .xlsx that actually computes the three-price transparency landed cost per trim path. When a user opens the file, marks the target-build features on the Inputs tab, and adjusts labor rate, they see landed cost per config recompute live.

Deliverables (committed on branch analysis-trim-path-impl):

1. `src/engine/xlsx.py` — minimal extension
   - Per the design's "one place a new xlsx.py helper is justified": add either a `include_provenance: bool = True` parameter to `write_data_table` OR a sibling `write_plain_table` function. Pick one and be consistent.
   - Do NOT add a formula-writing helper. Formulas are just strings assigned to `ws.cell(...).value` — openpyxl preserves them. The design says as much.

2. `src/engine/workbook.py`
   - Append Labor Rate ($/hr) to the INPUT_ROWS structure. Default value: 120. Attach `Input_Labor_Rate` named range (the pattern already exists for the other Input_* named ranges).
   - Render the Target_Build section below the single-cell inputs block. Header row + explanatory subheader + a plain (no-provenance) Excel Table named `Target_Build` with two columns: `Feature`, `Include`. Seed the table from the mod-pricing coverage (read `engine.data.mod_pricing`'s id→name map — the design's implementation notes call this out). Initial Include values default to "No". Attach a Yes/No data-validation dropdown to the Include column.

3. `src/engine/analysis/trim_path.py`
   - Replace the title-only `setup_formulas(ws)` with the two-table build per the design's "Analysis_TrimPath layout" section:
     - Enumerate 28 configs from `engine.data.trims.load()` (or re-read the order guide)
     - Enumerate 20 covered features from `engine.data.mod_pricing` (id→name map)
     - Write TrimPathDetail Excel Table (560 rows) with per-column formulas from the design's "Formulas per cell type" section — every formula uses structured references (no `$A$2` patterns)
     - Write TrimPathSummary Excel Table (28 rows) with its per-column formulas
     - Number-format the dollar columns (Base_MSRP, Aftermarket_Cost, Aftermarket_Labor_Cost, Landed_Cost, Delta_vs_Cheapest) for legibility

4. Tests — implement all 9 assertions from the design doc's "Test cases for IC #19 to validate against":
   - Sport / Willys / Rubicon landed values within $50 of the worked example ($48,890 / $54,390 / $58,350)
   - $5k calibration guard rail: Sport-mods landed < Rubicon-at-target landed by at least $5,000
   - No hardcoded cell addresses: grep every formula string for `\$[A-Z]+\$[0-9]` → 0 hits
   - Trims_MSRP named range still resolves to `Trims[MSRP]`
   - Standard-on delimiter safety: Sport is NOT counted standard for a feature whose Standard_On is "Sport S, Willys, Rubicon, Rubicon X"
   - Two Analysis tables exist (TrimPathSummary 28 rows, TrimPathDetail 560 rows)
   - Refresh preserves target-build Include values
   
   Because openpyxl doesn't calculate formulas, use the design's recommended approach: recompute expected values in Python from the same source data (trims + features + mod_pricing) and assert against the arithmetic; separately assert the formula strings use structured references only.

Success criteria (all must be true before commit):
- pytest passes green (77 baseline + new assertions), no skips
- ruff check passes clean
- engine render produces a valid .xlsx that opens cleanly
- The Trims_MSRP named range still resolves after render
- Formula strings in Analysis_TrimPath contain no `$[A-Z]+$[0-9]` patterns
- README updated only if genuinely necessary — the plug-in pattern likely doesn't shift for this IC

Scope boundaries:
- Do NOT design anything new — the design doc is authoritative. If you find a gap, flag it and choose the most conservative option; don't rewrite the design.
- Do NOT fix the "Data issues noted for a follow-on IC" items (body-agnostic ModPricing, factory-option gaps, winch prerequisite) — those are future ICs.
- Do NOT touch Data_Trims, Data_Features, Data_ModPricing, or other data modules
- Do NOT wire Data_Options (that's a separate future IC)
- Do NOT design formulas for other Analysis_* tabs (Sourcing, Financing, etc.)

Git:
- Work on branch `analysis-trim-path-impl` (create it: `git checkout -b analysis-trim-path-impl`)
- Commit incrementally with clear messages (workbook edits → xlsx helper → trim_path implementation → tests)
- Do NOT push to origin, do NOT merge to main, do NOT delete the branch
- Return the branch name in your final message

Time budget: substantial — this is the vertical-slice proof point and touches four Python files plus tests. The design doc handles the specification; you're doing mechanical implementation. Prioritize matching the design exactly; deviations should be rare and documented in commit messages.
```

---

## #8 — Build decomposition engine + per-layer sub-models

- **Spawn when:** provenance framework locked (#4) AND #6 (config data) complete AND aftermarket parts pricing sourced
- **Agent type:** `general-purpose`
- **Branch:** `decomposition-engine`
- **Output:** `calc/` directory with sub-models + tests
- **Status:** SKELETON — prompt to be written when dependencies clear

Scope reshape (per finding #8, 2026-07-17): builds per-decision-layer decomposition, NOT ranked TCO scenarios. Sub-models compute cost impact per axis (trim path + three-price features; sourcing delta; financing math with cash-vs-finance mechanism; timing/incentive; ongoing costs by category; risk-flag placement). Composite scoring rejected.

Sub-models take horizon N and personal inputs as **runtime parameters**, not build-time values. Same engine renders for any N and any personal-input file.

Blockers:
- Locked provenance schema (#4)
- `config/order_guide.json` from #6
- Aftermarket parts pricing source (for three-price feature transparency)

Not blockers (runtime inputs):
- Personal inputs from #7 (schema needed for interface; specific values not)
- Horizon N (parameter, not lock)

---

## #9 — Price used entries as sourcing/condition-layer alternatives

- **Spawn when:** #5 (source validation) complete AND #8 (decomposition engine) complete
- **Agent type:** `general-purpose`
- **Branch:** `used-entries`
- **Output:** `scenarios/used_entries.md` + `scenarios/index.yaml`
- **Status:** SKELETON — prompt to be written when dependencies clear

Scope reshape (per finding #8): used entries are alternative paths in the condition/sourcing layer, not a separate ranking exercise. Prices the 3 canonical used entries via Edmunds and slots them alongside new paths in the layer's transparency section. Tier 1 escalation trigger (within $3k or 10% monthly of best new path) still applies.

Blockers:
- Sources validated by #5
- TCO framework from #8
- 4xe scope decision (determines whether scenario 3 is modeled)

---

## #10 — Generate v1 decomposition report

- **Spawn when:** #7 (personal inputs) captured AND #8 (decomposition engine) AND #9 (used entries) complete
- **Agent type:** `general-purpose`
- **Branch:** `report-v1`
- **Output:** `report.md` (the one artifact)
- **Status:** SKELETON — prompt to be written when decomposition outputs exist

Scope reshape (per finding #8): report is organized by decision LAYER (transparency sections), not by scenario ranking. See spec.md "Report shape" for the five-section structure: (1) target build invariant, (2) biggest levers sized in dollars, (3) per-layer transparency sections with mechanism visible, (4) sensitivity, (5) provenance summary. No composite score, no named winner — decomposition that lets the user see the answer.

Blockers:
- All sub-models and scenarios modeled
- Weighting philosophy locked
