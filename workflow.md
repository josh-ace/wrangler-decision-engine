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
