# Prior Art Investigation — Does Anything Already Do This?

**Question:** Does any existing product, tool, framework, or service materially displace ≥50% of the Wrangler decision engine's function as defined by `spec.md`?

**Answer: No. Nothing surveyed displaces more than ~20%.** The verdict is **build**, with targeted adoption of two community data artifacts and one design idea. Confidence is high — four independent research passes (consumer products, commercial/professional TCO, open source, Wrangler community) converged on the same structural finding.

**Investigated:** 2026-07-16 · Method: web research across caredge.com, vincentric.com, jdpowervalues.com, edmunds.com, kbb.com, consumerreports.org, GitHub, JLWranglerForums, WranglerForum, JKOwners, Reddit, DOE AFDC.

---

## The structural finding

Every candidate falls into one of three categories, and **none of the three is the engine**:

1. **Data products** — price a *single configuration* at a time (CarEdge, Edmunds TCO, KBB, Vincentric, the JLWranglerForums order guide).
2. **Execution services** — negotiate or broker *one already-chosen deal* (CarEdge Concierge, AI Negotiator, CR Build & Buy, Authority Auto).
3. **Fleet/commercial engines** — real multi-scenario machinery, wrong domain (T3CO).

The engine's core function — **ranking heterogeneous acquisition scenarios against each other for one specific buyer** — is not what any of them do. The market has data *inputs* and it has purchase *execution*, but the decision layer between them is where every product stops and hands the problem back to the buyer. That is the gap the engine occupies, and it's the whole engine, not a corner of it.

The single sharpest illustration: **not one tool surveyed can answer "new Sport + mods vs. new Rubicon,"** despite this being the most-repeated question in Wrangler buying. It's re-derived by hand, from scratch, in forum thread after forum thread, going back to the JK generation.

---

## Candidate 1 — CarEdge (caredge.com)

The strongest consumer candidate, and the closest thing to a competitor. Formerly YAA / Your Auto Advocate (Ray & Zach Shefska).

**What it is / access model.** A tiered data + service product:

| Tier | Price | What you get |
|---|---|---|
| Free | $0 | Generic invoice price, target discount, listing search, calculators (depreciation, insurance, loan, lease, OTD), per-model 5-yr cost pages |
| Data | $9.99/mo | Market insights, fair-price evaluations |
| Pro / Insights | $39.99/mo | CarEdge Fair Price, Market Days Supply, total for-sale/sold counts, Black Book valuation, "CarEdge Recommendation," 10 reports/mo, up to 10 OTD quotes/mo |
| AI Negotiator | $49.99/search | AI emails dealers, negotiates OTD, one-shot |
| Concierge | $999/search | Human expert runs the deal end-to-end, one-shot |

**What's behind the paywall (verified directly).** Per-VIN/ZIP market intelligence: Black Book valuations, real transaction history, inventory-supply metrics that signal dealer motivation. It is a **negotiation-leverage product** — its purpose is to help you win the deal you have already decided to make.

**Dimensions addressed:**
- *Provenance* — **partial, weak.** Black Book is a real named source. But the free invoice tool carries only a blanket accuracy disclaimer with no date stamp, and `/jeep/wrangler/costs` cites "industry's leading data providers" and "EPA estimates" with **no source links and no `as_of` date on any value**. Fails the spec's minimum bar (`source` + `as_of_date` per value).
- *Re-runnable* — **yes for subscriptions** (live, re-queryable), **no for services** (explicitly per-car-search).
- *TCO* — **fixed 5-year only**, one configuration, hardcoded assumptions (40-yr-old driver, 72-mo @ 6.99%, 20% down, 15k mi/yr). Sub-calculators are adjustable; the TCO rollup is not. No user-set horizon → cannot serve the spec's open 3/5/8-yr lock.
- *Sourcing channel* — out-of-state is listed as *covered* by the services ("we'll handle it if it comes up"), not modeled as a comparable option with a quantified delta.

**Does NOT address:** multi-axis scenario ranking · mod-adjusted target-build math (zero evidence anywhere) · national-delivery discount dealers as a first-class priced scenario · MY2026-vs-MY2027 timing fork · recall/defect risk register · Wrangler trim-level depth (**the Wrangler costs page has no trim breakdown at all** — Sport and Rubicon are the same number) · any API or structured export (a community thread literally asks "Where's the Spreadsheet").

**Displacement: ~15%.** Overlaps on generic cost inputs, which discovery pass #5 already sourced anyway.

## Candidate 2 — JLWranglerForums community artifacts

Two durable artifacts, both **pure reference data, not calculators**:

1. **Order Guide & Price List Interactive Spreadsheet** — the community's annual conversion of Jeep's internal dealer order guide. MSRP + invoice by trim and option code, "as optioned" totals. Maintained ad hoc by volunteers; thread lineage back to 2021. **Notably, it self-caveats:** the thread states it reflects a specific month's order guide and goes stale within weeks as packages and pricing shift.
2. **"Ratbert's Dealers Below-Invoice Spreadsheet"** (40+ pages) — crowdsourced list of which dealers nationally sell at X% below invoice, plus affiliate-discount stacking (e.g. Tread Lightly +1%).

**Dimensions addressed:** Config & MSRP data (class #1) · discount-dealer *identification* (class #5, partially).
**Does NOT address:** any calculation whatsoever. No TCO, no financing, no ranking, no scenario logic beyond summing option codes.
**Re-runnable:** No — manually re-derived once per model year.
**Provenance:** Informal but real — sourced to a named month's order guide. This is *better* provenance discipline than CarEdge, ironically.

**Displacement: ~10%** (as input data, which the engine already consumes at `config/order_guide.json`).

## Candidate 3 — T3CO (github.com/NatLabRockies/T3CO)

The only genuine open-source *engine* found. DOE/NREL-funded, BSD-3, Python, actively maintained (last push 2026-07-14, v2.0 this year).

**Why it's interesting:** architecturally it's the right shape. Driven by three input files (Vehicles, Scenarios, Config), ships 500+ pre-built vehicle-scenario pairs, supports batch "sweep" runs. It even has *partial vintage-tracking*: fuel-price inputs are tagged to a specific EIA Annual Energy Outlook year/case rather than a frozen number.

**Why it doesn't displace:** wrong domain, decisively. It targets **commercial/heavy-duty fleets** — drive cycles, gradeability, range, powertrain optimization. "TCO" there means capital + fuel + maintenance for a fleet operator. **No financing/lease/cash comparison, no condition/trim/sourcing-channel axes, no consumer purchase-structuring.** Adapting it would mean discarding everything it does and keeping only the sweep-runner — cheaper to write from scratch.

**Displacement: ~5%.**

## Dismissed with reasons

- **Vincentric** — B2B only (OEM/fleet/dealer licensing). No consumer portal, no self-serve checkout, pricing unpublished. Real 8-factor TCO model, unreachable. Single Vehicle Reports exist but require sales contact.
- **ALG / J.D. Power Valuation Services** — B2B/institutional (insurers, lenders, tax assessors). Feeds lease residuals invisibly; no consumer path.
- **Edmunds TCO** — live for MY2026, solid factor coverage. But compares **vehicles, not acquisition methods** — every scenario is assumed new-purchase-financed. Edmunds itself states "TCO is a comparative tool, not a predictive tool." Still valuable as an *input* (spec already uses it for Tier 2).
- **KBB 5-Year Cost to Own** — same pattern as Edmunds; fetch-blocked (403), specifics unconfirmed.
- **Consumer Reports Build & Buy** — not a TCO tool at all; a TrueCar-powered dealer-quote service.
- **Fleet software** (Element, Wheels/Donlen, Fleetio) — enterprise-only. Fleetio's free public TCO calculator is technically usable but models fleets, not acquisitions.
- **Concierge/brokers** (Authority Auto ~$495–1000, Car Concierge Plus) — execute a purchase, never rank paths to it.
- **Autocosts** (GitHub, GPLv3) — stalled since Dec 2024, single-scenario consumer cost calculator, no provenance.
- **DOE AFDC Vehicle Cost Calculator** — not open source; one fixed financing scenario; several inputs date to ~2010–11.
- **Mark Dodge / Granger** — quote forms and a generic payment calculator. No comparison tooling.
- **Aftermarket build tools** (Quadratec, ExtremeTerrain 3D builder) — shopping carts. They total parts but never connect back to trim choice.
- **Toy repos** (`chgallegos/TCO-App`, `jgeorgex/car-tco-calculator`, `unhurried`, `martamateu`, `ErezNagar/lease-calculator`) — demos, single-scenario, no provenance.

---

## Recommendation: **BUILD**

Not "adapt-existing," not "build-only-for-gap" — because **the gap is the engine itself**, not a missing corner of something that exists.

The reasoning: prior art is dense at the two ends and empty in the middle. Data inputs are well-covered (and discovery pass #5 already mapped them). Purchase execution is well-covered and buyable. The decision layer — multi-axis ranking, mod-adjusted build math, provenance-tracked and re-runnable — has **no occupant at any price**, including $999 concierge and B2B-licensed Vincentric. No candidate exceeds ~20% displacement, and no two candidates compose into the engine, because none of them share a data model or expose an API.

Adoption is limited to **inputs, not machinery**:
- **Adopt** the JLWranglerForums order-guide spreadsheet as a cross-check against `config/order_guide.json` — with its stated month captured as `as_of_date`.
- **Adopt** Ratbert's below-invoice dealer list to seed and validate variable class #5 (national-delivery discount dealers).
- **Optionally subscribe** to CarEdge Pro ($39.99, one month, cancellable) *at the finalist stage only* — Market Days Supply and Black Book valuation are genuine negotiation inputs the engine can consume. This is buying a data feed, not adopting a tool.

## Design ideas worth stealing

1. **T3CO's three-file input split (Vehicles / Scenarios / Config).** Independently validates the spec's separation of scenario definition from parameters, and its sweep-runner shape is exactly what "re-runnable as market conditions change" needs.
2. **T3CO's vintage-tagged inputs** — fuel price bound to "AEO 2025 reference case" rather than a frozen number. Generalize this: provenance should be able to name a *published dataset edition*, not just a URL + date. Feeds open lock #4.
3. **CarEdge's Market Days Supply** — a leverage/negotiability metric the spec's taxonomy doesn't currently carry. Fits naturally in class #15 (inventory/timing) and informs achievable discount, not just list price.
4. **The forums' Sport-vs-Rubicon reasoning is the engine's own math, done by hand.** Threads converge on a real decision rule: Rubicon wins below 37s / no-regear goals; built Sport wins only at 40"+ requiring Dana 60s. Typical line items: regear ~$2k, tires/wheels ~$2–2.25k, lift ~$1.5k, plus locker cost vs. Rubicon premium. **Use these as calibration test cases** — if the target-build parameter can't reproduce the community's conclusion at its own inputs, it's wrong.
5. **CarEdge's stated-assumption block** (driver age, APR, term, mileage split) is a good UX pattern executed with bad rigor — it states assumptions but never dates or sources them. The engine's assumption log should render like this and then actually cite.

## Confidence & limits

High confidence on the verdict; the finding is structural, not marginal, and four independent passes agreed. Two caveats, neither load-bearing: CarEdge's `/plans/insights` page is a JS-rendered SPA that resisted direct fetch, so the Data ($9.99) vs. Pro ($39.99) tier boundary rests partly on secondary sources — but the $39.99 feature list was confirmed across the `/pro` page and independent reviews, and no plausible tier content would change the verdict, since the failure is categorical (a data feed is not a ranking engine). KBB and Edmunds blocked WebFetch with 403s; their specifics come from help docs and search results rather than live pages — both are already scoped as engine *inputs*, not competitors.
