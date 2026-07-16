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

## #8 — Build TCO framework + acquisition sub-models

- **Spawn when:** provenance framework locked AND #6 (config data) complete
- **Agent type:** `general-purpose`
- **Branch:** `tco-framework`
- **Output:** `calc/` directory with sub-models + tests
- **Status:** SKELETON — prompt to be written when dependencies clear

Blockers:
- Locked provenance schema
- Locked time horizon
- `config/order_guide.json` from #6

---

## #9 — Model Tier 2 canonical used scenarios via Edmunds

- **Spawn when:** #5 (source validation) complete AND #8 (TCO framework) complete AND 4xe scope locked
- **Agent type:** `general-purpose`
- **Branch:** `used-baseline`
- **Output:** `scenarios/used_baseline.md` + `scenarios/index.yaml`
- **Status:** SKELETON — prompt to be written when dependencies clear

Blockers:
- Sources validated by #5
- TCO framework from #8
- 4xe scope decision (determines whether scenario 3 is modeled)

---

## #10 — Generate v1 report + assembly

- **Spawn when:** personal inputs captured AND #8 AND #9 complete
- **Agent type:** `general-purpose`
- **Branch:** `report-v1`
- **Output:** `report.md` (the one artifact)
- **Status:** SKELETON — prompt to be written when scenario outputs exist

Blockers:
- All sub-models and scenarios modeled
- Weighting philosophy locked
