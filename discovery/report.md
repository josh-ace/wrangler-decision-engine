# Discovery Pass — Variable Taxonomy + Source Validation

**2026 Jeep Wrangler Decision Engine · Workflow prompt #5**
**Date:** 2026-07-15 · **Scope:** source discovery & taxonomy validation only. No data collected, no purchase/trim/config recommended.

> **How to read confidence flags.** Every source claim carries **HIGH** (verified live this session), **MEDIUM** (source identity confirmed; a specific field/number recalled or partially verified), or **LOW** (plausible/inferred, needs confirmation). Confidence is about the *source-validation claim*, never about any dollar figure — no figures were collected.

---

## 0. Executive summary — what changed vs. the draft taxonomy

Five findings that should propagate into the engine before modeling begins:

1. **The 4xe federal tax credit is DEAD as a live 2026 variable.** The One Big Beautiful Bill Act (P.L. 119-21, signed 2025-07-04) terminated §30D (new clean vehicle), §25E (used), and §45W (commercial — the lease "loophole") for vehicles **acquired after 2025-09-30**. IRS.gov confirms this directly (page effective 2026-07-13). The taxonomy's "Tax credits" row must be reclassified: **federal = expired; state-only remains** (Colorado the standout PHEV incentive). Watch a stale-data trap: dealer/blog pages and even Stellantis marketing still cite "$7,500 on a 4xe lease" — that is now a *manufacturer* incentive, **not** a federal credit, and must be modeled as dealer cash, not tax. **[HIGH]**

2. **"Sourcing channel" needs the national-delivery discount-dealer pattern as a first-class scenario.** Mark Dodge (LA) and Granger Motors (IA) publicly quote **~7% below invoice** on 2026 Wranglers with price protection, ~$1k deposit, nationwide delivery, ~10–16 wk lead time. This is a distinct acquisition path with a *quantifiable* price delta vs. local — the draft under-weights it. **[HIGH]**

3. **A Wrangler-specific timing fork exists: MY2026 is likely the last-of-V6/manual before a 2027 facelift + Hurricane I6 re-power.** This is a discrete timing scenario (end-of-run incentives + last easy shot at the 3.6 V6/manual vs. wait for a refreshed, re-powered, likely-pricier 2027). Generic frameworks miss it. **[HIGH on facelift/lineup; MEDIUM on exact V6-drop timing]**

4. **A recall/reliability *risk register* is missing from the taxonomy entirely.** The community actively tracks: 4xe high-voltage battery **fire recall** (expanded Nov 2025 to ~228k units, active class action, park-outside guidance), **death wobble** (still reported on 2024–25 stock units), **UConnect 5** black-screen/OTA failures, a **TPMS recall** (~79k units), and **Sky One-Touch top leaks**. These are config-conditional risk flags with real TCO and resale consequences. **[HIGH]**

5. **Powertrain (3.6 V6 · 2.0T · 4xe) is not just a config line-item — it's the central Wrangler fork** carrying distinct reliability, fuel, resale, warranty (4xe battery 8yr/100k), and now tax profiles. It deserves to be a cross-cutting dimension the engine reasons about, not a single MSRP delta.

---

## 1. Refined variable taxonomy

Legend: **✚ added** · **✎ corrected/re-scoped** · **⚑ flagged uncertain** · (unmarked = validated as-is)

| # | Class | What it captures | Status | Primary source(s) | Refresh |
|---|---|---|---|---|---|
| 1 | Config & MSRP | Trim, packages, options, invoice, **holdback (~3% MSRP, computable)** | ✎ add invoice+holdback | Order guide PDFs; jlwranglerforums 2026 order-guide spreadsheet; autocheatsheet | Once/MY |
| 2 | Manufacturer incentives | Customer/retail cash, APR subvention, lease cash, loyalty/military/first-responder | ✓ | Jeep.com incentive lookup (ZIP) + CarsDirect + forum deal threads | Monthly |
| 3 | Lease programs | Money factor, residual % by term/mileage/region | ✓ | Edmunds lease megathread; 4xeForums lease thread | Monthly |
| 4 | Real transaction prices | % off MSRP, dealer discount patterns, deal-quality rating | ✎ broaden beyond TrueCar | CarGurus IMV/Deal Rating; forum deal reports; TrueCar (lead-gen caveat); KBB Fair Purchase Price | On-demand / weekly |
| 5 | Bulk / national-delivery dealer pricing | Advertised % below invoice, price protection, delivery, lead time | ✎ elevate to scenario axis | Mark Dodge (per-VIN, public), Granger, Koons, Criswell, Aventura | On-demand |
| 6 | Depreciation / residual | JL-specific curves; **ALG best-in-class residual award**; residual % as model input | ✎ add residual-award signal | iSeeCars; KBB/Edmunds Cost-to-Own; Manheim (index public, VIN-level dealer-only) | Yearly / monthly index |
| 7 | Fuel economy | Real-world vs EPA, by powertrain; 4xe MPGe + electric range | ✎ add 4xe electric fields | EPA fueleconomy.gov (free API); Fuelly | Once/MY |
| 8 | Insurance | Personalized premium per config; aggregator averages as pre-quote proxy | ✎ add proxy layer | Personalized quote (finalist); The Zebra/ValuePenguin/MoneyGeek (proxy) | Once/finalist |
| 9 | Maintenance | Scheduled-service intervals (Normal/Severe), by powertrain; typical costs | ✓ | Mopar owner's-manual PDF (primary); RepairPal; KBB schedule | Once/MY |
| 10 | Reliability | Common issues, ratings, **recall/TSB register (see #18)** | ✎ split out risk register | RepairPal, CR (paywall), J.D. Power, NHTSA API, forums | Once + on recall |
| 11 | Tax / reg | Home-state (often county) use tax, out-of-state titling, doc fee (dealer-state), **annual personal-property/ad-valorem tax** | ✎ clarify state vs. county | State DOR/DMV; WalletHub (property tax); CarEdge (doc fee) | Once + on rule change |
| 12 | Tax credits | **Federal §30D/§45W EXPIRED (acquired >2025-09-30)**; state PHEV credits only | ✎ MAJOR re-scope | IRS.gov clean-vehicle page; CO Energy Office/DOR; DOE AFDC | On rule change |
| 13 | Mod costs | Parts pricing for target build; **install labor = shop quote (not public)** | ✎ note labor gap | Quadratec, Northridge4x4, ExtremeTerrain, Morris4x4; local shop | On build change |
| 14 | Warranty | Factory terms (3/36, 5/60, corrosion, roadside); **4xe HV battery 8yr/100k**; Magnuson-Moss mod interaction | ✎ add 4xe battery + MMWA | jeep.com/warranty; FTC (MMWA); Mopar | Once |
| 15 | Inventory / timing | Stock levels, days-on-lot, **MY2026→2027 changeover fork** | ✎ add MY-changeover | Jeep inventory; dealer sites; TFL/MoparInsiders (MY news) | Weekly (decision window) |
| 16 | Personal | Budget, credit, mileage, use case, trade-in value, home state/county | ✓ | User | Static |
| 17 | Used market (Tier 2) | TMV, TCO, private-party/dealer values | ✓ | Edmunds; KBB | Monthly |
| **18** | **✚ Recall / defect risk register** | 4xe fire recall, death wobble, UConnect 5, TPMS recall, Sky-top leaks — config-conditional risk flags | ✚ NEW | NHTSA API (recalls/complaints/investigations); forums; class-action trackers | On-demand + on recall |
| **19** | **✚ Powertrain profile** | 3.6 V6 vs 2.0T vs 4xe as cross-cutting dimension: reliability, fuel, resale, warranty, tax, availability | ✚ NEW (cross-cutting) | Composite of #6–14 keyed by engine | Derived |
| **20** | **✚ Config availability / MY constraints** | Trim×body-style legality (some trims 4dr-only), manual only w/ V6, "Late Availability" combos, 4.88 axle requires manual | ✚ NEW | Order guides; MoparInsiders/JeepSpecs buyers guides | Once/MY |
| **21** | **✚ Emissions / CARB jurisdiction** | CARB vs. 49-state config/availability + 4xe battery-warranty extension in CARB states | ✚ NEW (was a spec gap) | Jeep order guide fine print; CARB; state rules | Once |

**Resolution of the spec's "Known gaps to validate":**

| Spec gap | Verdict | Where it lands |
|---|---|---|
| Dealer add-ons & doc fees (state-regulated) | **Confirmed real; partly public.** Doc-fee caps aggregated (CarEdge); mandatory add-ons NOT centrally published | Class #11 + on-demand quote |
| Extended warranty pricing | **Quote-only.** Mopar plan terms public, price requires VIN+mileage quote | Class #14; model as range |
| GAP insurance mechanics | **Quote-only across all channels** (dealer F&I, insurer rider, credit union — CU usually cheapest) | Class #8/#14; model as range |
| Opportunity cost of custom-order wait | **Real, quantifiable.** ~10–16 wk order lead time; pair with price-protection terms | Class #5 + #15 (timing) |
| CARB vs 49-state emissions | **Confirmed as a variable** → promoted to new class #21 | Class #21 |
| Financing gotchas (prepay penalty, mandatory add-ons) | **Real; quote-only.** Surfaces in dealer F&I, not centrally published | Class #2/#11; finalist-stage |
| Trade-in value modeling | **Sourceable** (KBB/Edmunds trade-in vs private-party vs dealer-retail cuts) | Class #16/#17 |

---

## 2. Source candidates per variable class

### 2.1 Pricing, incentives, transaction prices, lease programs (classes 1–5)

| Source | Access path | Specific fields provided | Access mechanism | Refresh | Reliability / bias | Conf. |
|---|---|---|---|---|---|---|
| **Jeep.com incentive lookup** | `jeep.com/incentives.wrangler.html` (ZIP-filtered); `/incentives/military-incentive.html`, `/first-responder.html` | Retail/customer cash; APR rate×term (Stellantis Financial); advertised lease payment/term/DAS; loyalty/conquest bonus; military $500; first-responder $500; offer-end date | Public web, no login | **Monthly** (resets ~1st; regional "BC" offers differ by ZIP) | Authoritative for *advertised consumer* incentives. Does NOT show dealer discount off MSRP, dealer cash, or stack rules | HIGH |
| **Edmunds lease megathread** | `forums.edmunds.com/discussion/74087/...2026-jeep-wrangler-lease-deals...` | **Money factor** (e.g. .00178-shape), **residual %** by term (24/36/39/48) × mileage (10k/12k/15k), region/ZIP, lease-cash notes | Public read; free login to post a request | **Monthly** (Stellantis programs) | Key input for lease math. Host-answered → coverage lags for slow trims; self/host-reported, verify vs dealer. **Edmunds 403s automated fetch — needs browser** | HIGH (thread active); MEDIUM (mechanics) |
| **4xeForums lease thread** | `4xeforums.com/threads/stellantis-lease-money-factor-residuals.7314/` | 4xe-specific MF + residuals; cross-check to Edmunds | Public read | Monthly | Best 4xe lease datapoint source | HIGH |
| **CarsDirect Deals** | `carsdirect.com/jeep/wrangler/prices-deals` + monthly roundups | Cash back (total + by trim); APR rate/term/lender; lease payment/term/DAS/mileage; their "Effective Cost/mo"; rebate-vs-APR tradeoff | Public, no login | "Updated daily"; timestamped | **Lead-gen/affiliate**; numbers are national-headline, not your-ZIP | HIGH |
| **KBB** | `kbb.com/jeep/wrangler/2026/...` + `/cost-to-own/` + appraisal | **Fair Purchase Price** (new, what buyers pay); Fair Market Range; used trade-in / private-party / dealer-retail; **5-Year Cost to Own** (7 buckets) | Public, free | Fair Purchase ~weekly; CtO per MY | Cox Automotive-owned (Autotrader/Manheim/Dealertrack); trade-in skews conservative; proprietary method | HIGH |
| **CarGurus** | `cargurus.com`; `/research/car-valuation` | **Instant Market Value (IMV)** (70+ data points, daily); **Deal Rating** (Great/Good/Fair/High/Overpriced vs IMV); price history & days-on-lot on listings | Public, free; login optional | IMV daily; listings near-real-time | IMV is asking-price-derived (can lag sold prices); Deal Rating factors opaque "dealer reputation"; sponsored placement | HIGH (IMV/rating); MEDIUM (price-history/DOL) |
| **TrueCar** | `truecar.com` (also credit-union white-labels) | "What others paid" distribution; target price; Guaranteed (or "Estimated" in some states) Savings Certificate | Public; **contact info required** to unlock cert | Transaction-driven | **Heavy lead-gen** (~$50/lead to dealers); certified-dealer network only → misses aggressive out-of-state discounters | HIGH |
| **Mark Dodge** | `markdodge.net` (per-VIN inventory) | **Per-VIN "Mark Dodge Discount"** + national/regional bonus cash, totaled (e.g. ~14–15% off shape); free delivery ≤250 mi | Public web, per-listing | Continuous (inventory) | Most transparent discounter — actual discount on the listing | HIGH |
| **Granger / Koons / Criswell / Aventura** | Forum group-buy threads + dealer sites | **Advertised % below invoice** (Granger ~7%; Koons/Criswell tiered — verify 2026); price protection; deposit; nationwide TTL | Headline public (often via forum); **exact OTD = direct quote** | On-demand | Granger HIGH; Koons MEDIUM; Criswell LOW–MEDIUM; Aventura LOW — historical %s need 2026 re-confirmation | Mixed |
| **Invoice + holdback** | jlwranglerforums 2026 order-guide spreadsheet; autocheatsheet; rydeshopper | Invoice-vs-MSRP by trim/option code; **holdback ~3% of total MSRP** (published convention, computable) | Public (forum spreadsheet highest-trust); aggregators often lead-gen-gated | Once/MY | Forum spreadsheet best free option; aggregators can be stale. **Dealer cash/stair-step = NOT public** | HIGH (findable); MEDIUM (aggregator accuracy) |

### 2.2 Ownership cost — depreciation, fuel, insurance, maintenance, reliability (classes 6–10)

| Source | Access path | Specific fields | Access | Refresh | Reliability / bias | Conf. |
|---|---|---|---|---|---|---|
| **iSeeCars depreciation** | `iseecars.com/car/jeep-wrangler/resale-value` | Depreciation % at 3/5/7/10 yr + projected $ resale; **separate rows for standard vs 4xe**; segment comparisons; best/worst-resale rankings | Public, free | ~Annual study | Modeled projection (not sold transactions); no trim/mileage granularity; asking-price-based; Wrangler flattered (real, but note) | HIGH |
| **Edmunds / KBB Cost-to-Own** | `edmunds.com/jeep/wrangler/2026/cost-to-own/`; `kbb.com/.../cost-to-own/` | 5-yr total broken into **Depreciation, Insurance, Financing, Fuel, Maintenance, Repairs, Taxes/Fees**; per-year + 5-yr; configurable by body/trim/powertrain | Public, free | Rolling (~monthly stamp) | **Modeled national averages** (assumes ~15k mi/yr, generic driver); the two models disagree; not a substitute for a real insurance quote; 4xe breakouts can lag at launch | HIGH (fields); MEDIUM (4xe completeness) |
| **Manheim** | Public: MUVVI at `site.manheim.com/.../used-vehicle-value-index.html` / coxautoinc.com. Industry: MMR (dealer login) | Public = single national wholesale index (level, MoM%, YoY%, segment commentary; **not Wrangler-specific**). MMR = VIN/trim/mileage wholesale values | Public index free; **MMR = licensed-dealer paid** | Index monthly + mid-month; MMR continuous | Wholesale ≠ retail; the Wrangler-specific number you'd want is behind the dealer wall | HIGH (split/cadence) |
| **Fuelly** | `fuelly.com/car/jeep/wrangler` | Crowd-sourced avg MPG + sample size + total fuel-ups/miles; segmentable by MY and engine (3.6 / 2.0T / 4xe); per-owner logs | Public but **scrape-hostile (403)** | Continuous | Self-selection (enthusiasts, big tires → skews low); unverified entries; thin newest-4xe samples. Directional vs EPA | MEDIUM |
| **EPA fueleconomy.gov** | UI `fueleconomy.gov/feg/bymake/Jeep2026.shtml`; **free API `/ws/rest/...`, no key, JSON/XML** | city/hwy/combined MPG; **4xe: MPGe, gas-only MPG, electric range, kWh/100mi, fuel-type flags, annual fuel cost, GHG/smog**; EPA "My MPG" crowd layer; bulk CSV | Public, free, **no key** | Per MY at certification | Lab values (optimistic); main risk is matching exact trim ID. Authoritative, unbiased | HIGH |
| **Insurance aggregators** | The Zebra `/vehicles/jeep/wrangler/`; ValuePenguin; MoneyGeek; Insure.com; Compare.com | Avg annual/monthly premium; full-coverage vs liability; by model year / driver age / state / insurer (cheapest-carrier tables); trim influence usually qualitative | Public, free (modeled) | Periodic (annual–quarterly) | Each uses a different hypothetical driver → not mutually comparable; lead-gen; 4xe rarely isolated. **Real number needs a personalized quote** | HIGH (landscape) |
| **RepairPal** | `repairpal.com/reliability/jeep/wrangler` | Reliability rating /5 + segment rank; avg annual repair+maint $; visit frequency/yr; severe-repair probability %; ranked common problems; per-job cost ranges | Public, free | Periodic | Shop-network aggregate (skews older/out-of-warranty; thin on brand-new 2026) | HIGH |
| **Consumer Reports** | `consumerreports.org/cars/jeep/wrangler/2026/...` | Predicted reliability, trouble-spots by system, owner-satisfaction %, road-test score, by MY | **Paywalled** (member) | Annual survey | Subscriber-survey self-selection; Wrangler historically rates low | HIGH (paywall) |
| **J.D. Power** | `jdpower.com/cars/2026/jeep/wrangler` | Quality & reliability, resale, driving-experience, dealership scores (/100 or /5); IQS/VDS/APEAL summaries | Public (consumer); full studies paid | Annual/study | Survey-based, segment-relative, generation-level not trim | HIGH |
| **NHTSA** | `nhtsa.gov/recalls`; **free APIs `api.nhtsa.gov`, `vpic.nhtsa.dot.gov`, no key** | Recall campaigns (component/remedy/dates); consumer complaints; open/closed ODI investigations; NCAP crash ratings; VIN decode; bulk datasets | Public, free, **no key** | Near-real-time | Authoritative, unbiased. **Best free structured API in the set** | HIGH |
| **Mopar maintenance schedule** | `mopar.com/om` portal; direct PDF `vehicleinfo.mopar.com/.../2026/Jeep/Wrangler/...pdf` | Normal + Severe-Duty interval tables: oil/filter, rotation, fluids, filters, plugs, belts — **per-powertrain** (2.0T/3.6/4xe) | Public, free (no login) | Per MY | OEM spec, no bias. Verify exact intervals against the PDF (KBB republishes a convenient table) | HIGH (location); MEDIUM (interval numbers) |

### 2.3 Tax, registration, credits (classes 11–12)

| Source | Access path | Specific fields | Access | Refresh | Reliability / bias | Conf. |
|---|---|---|---|---|---|---|
| **IRS clean-vehicle page** | `irs.gov/clean-vehicle-tax-credits` (effective 2026-07-13) | Confirms §30D/§25E/§45W **not available for vehicles acquired after 2025-09-30**; survives only if binding contract+payment ≤ that date | Public | On statute/guidance change | Authoritative. **The decisive 4xe-credit source** | HIGH |
| **Colorado Energy Office / CO DOR** | `energyoffice.colorado.gov/.../electric-vehicle-tax-credits`; `tax.colorado.gov/electric-vehicle-tax-credits` | Innovative Motor Vehicle Credit (PHEV eligible, ~$750 2026-shape, MSRP cap, lease vs purchase); income-gated VXC point-of-sale rebate | Public HTML+PDF | Per tax year (statutory) | Standout live state PHEV incentive; amount steps down over time | HIGH (identity); MEDIUM (2026 $) |
| **DOE AFDC** | `afdc.energy.gov/laws?state=XX` | Federal clearinghouse of state incentives — scan which states have a live PHEV incentive, then confirm at that state's DOR | Public | Periodic | Authoritative index; confirm dollar specifics at state source | HIGH |
| **State DOR / DMV (use tax + titling)** | e.g. CA CDTFA `cdtfa.ca.gov/.../vehicles.htm`; NV DMV `dmv.nv.gov/regoutofstate.htm`; per state | **Home-state use tax** rate (keyed to registration address) collected at titling; reciprocity/credit for tax paid elsewhere; MSO/MCO + temp-tag → title procedure; VIN/emissions inspection where required | Public HTML+PDF forms; **no API** | Irregular (on rate/statute change) | Per-state (FL/LA administer at county/parish). Two authorities per deal: dealer-state (temp tag) + home-state (final title). Some DOR pages undated (staleness) | HIGH (shape); MEDIUM (per-state numbers) |
| **WalletHub property-tax table** | `wallethub.com/edu/states-with-the-highest-and-lowest-property-taxes/11585` | Per-state **annual vehicle property/ad-valorem tax** effective rate + $ on standardized vehicle (VA ~3.97% high; CA/FL/TX/NY $0) | Public | Annual (Jan 2026 data) | Transparent methodology (Census + DMV); exact local rate is county-dependent | HIGH (identity); MEDIUM (local rate) |

### 2.4 Doc fees & dealer add-ons (class 11 cont.)

| Source | Access path | Specific fields | Access | Refresh | Reliability / bias | Conf. |
|---|---|---|---|---|---|---|
| **CarEdge doc-fee guide + State of Dealer Fees** | `caredge.com/guides/car-dealer-doc-fee-by-state`; `/reports/state-of-dealer-fees` | Statutory doc-fee cap (where one exists), state average + range; report built on 57k+ real OTD quotes (empirical). Capped: CA ~$85, NY $175, WA $200, MD $800. Uncapped/high: FL, VA, NC $700–999+ | Public HTML (feeds OTD calc); **no CSV/API** | Annual + quote-driven | Strongest *empirical* (actually-charged) source; mild lead-gen | HIGH (current); MEDIUM (per-state cap $) |
| **Mandatory/typical add-ons** | Empirical OTD-quote datasets + community deal threads | Nitrogen, paint/fabric protection, VIN etch, "market adjustment" | Not centrally published | — | Best evidence is real quotes + forum reports | MEDIUM/LOW |
| **State statute / DOR dealer-licensing reg** | Per state | Authoritative doc-fee cap (primary source behind aggregators) | Public | On statute change | Primary source; slower to read than aggregator | HIGH |

### 2.5 Mod parts pricing (class 13) — live-verified 2026

All four retailers are live in 2026 with public catalogs, no login, **no documented public API** (machine path = affiliate product feeds, not first-party API), and **none list install-labor dollars**. Every stored price needs a **capture date** — list prices are coupon/sale-driven.

| Source | Access path | Specific fields | 4xe fitment | Install info | Conf. |
|---|---|---|---|---|---|
| **Northridge4x4** | `northridge4x4.com` (year selector 1959–2026) | Itemized pricing; strong premium suspension/armor; **itemizes per-component pricing inside bundled kits** (best for granular cost modeling) | Weak (per-product only) | Labor not listed | HIGH |
| **Quadratec** | `quadratec.com` ("garage" selector, JL 2018–2026) | Itemized price/brand/part#/fitment/stock; ratings & reviews | **Strong — explicit fits/excludes-4xe flags (the fitment authority)** | Labor not listed | HIGH |
| **ExtremeTerrain (Turn 5)** | `extremeterrain.com` (JL 2018–2026) | Itemized pricing; ratings/reviews; how-to content; product-level exclusions | Good (product-level exclusions) | **Only source giving install *hours* + difficulty (partial SKUs); still no labor $** | HIGH |
| **Morris4x4Center** | `morris4x4center.com` | Itemized pricing; OEM + aftermarket; fitment filtering | Unknown | Labor not listed | LOW (**503 Cloudflare — resists automated fetch; secondary cross-check only**) |
| **Install labor** | Local 4x4 shop | Labor $ for lift/regear/armor install | — | **Quote-only** — apply local shop hourly rate to an hours estimate (ExtremeTerrain hours as a seed) | HIGH (that it's quote-only) |

All six requested mod classes (lift kits, wheels/tires, front/rear bumpers, winch, armor/skid/rock-rails, lighting) confirmed present on Northridge, Quadratec, and ExtremeTerrain. Use **Quadratec** as the reliable 4xe fitment authority; **Northridge** for granular per-component kit costing.

### 2.6 Warranty & protection products (class 14)

| Source | Access path | Specific fields | Access | Refresh | Reliability / bias | Conf. |
|---|---|---|---|---|---|---|
| **Jeep factory warranty** | `jeep.com/warranty.html` + VIN terms in owner Dashboard | Basic 3yr/36k; Powertrain 5yr/60k; Corrosion 5yr/unlimited; Roadside 5yr/60k; **4xe HV battery/hybrid 8yr/100k** (federal floor; possibly 10yr/150k in CARB states) | Public | Per MY | Authoritative | HIGH (standard terms); MEDIUM (CARB extension) |
| **FTC — Magnuson-Moss** | `ftc.gov/.../nixing-fix...`; `consumer.ftc.gov/articles/auto-warranties-service-contracts`; 15 U.S.C. §2301 | Aftermarket part can't blanket-void warranty; maker must **prove the part caused the specific failure**; FTC enforcement precedent | Public (consumer page 403s automated fetch) | Stable | Authoritative; in practice dispute burden falls on owner; related-driveline claims still at risk | HIGH |
| **Mopar Vehicle Protection (FlexCare)** | `mopar.com/en-us/care/flexcare-vehicle-protection.html` | Extended-service plan terms/coverage tiers public; **price = quote-only** (VIN+mileage) | Public terms; **quote-only price** | — | 3rd-party ballpark ~$700–5,000 up to 8yr/125k; dealer-marked-up/negotiable | HIGH (quote-only); MEDIUM ($) |
| **GAP** | Mopar MVP GAP; insurer rider; credit union/bank | Terms public; **price quote-only** (depends on loan amount/LTV/lender); CU often cheapest (~$200–400 flat) | Quote-only | — | Never publicly listed | HIGH (quote-only) |

### 2.7 Recall / defect risk register (class 18 — NEW)

| Source | Access path | Specific fields | Access | Refresh | Conf. |
|---|---|---|---|---|---|
| **NHTSA API** | `api.nhtsa.gov` (recalls/complaints/investigations); `nhtsa.gov/recalls` | Recall campaign (component, remedy, affected MY/VIN range, dates); complaint records; ODI investigations | Public, free, no key | Near-real-time | HIGH |
| **Forums (JLWranglerForums, 4xeForums, WranglerForum)** | see §3 | Owner-reported frequency & lived experience of: 4xe fire recall, death wobble, UConnect 5, Sky-top leaks, start-stop | Public read (403 to automated fetch) | Continuous | HIGH |
| **Class-action / legal trackers** | e.g. TopClassActions, law-firm recall pages | 4xe battery-defect suit status, park-outside guidance | Public | On filing | MEDIUM |

---

## 3. Community landscape check

### 3.1 Platforms (where the decision data actually lives)

| Platform | URL | Best for | Alive 2026? | Conf. |
|---|---|---|---|---|
| **JLWranglerForums** | `jlwranglerforums.com` | **Primary buying intel.** Ordering/Pricing/Tracking subforum = pinned annual **Order Guide & Price List** (MSRP+invoice per option code), national-delivery dealer deal threads (Mark Dodge, Granger), live order-to-delivery timelines; mods & problems subforums | Yes — threads into mid-2026 | HIGH |
| **4xeForums** | `4xeforums.com` | **4xe-specific**: battery degradation, charging-in-practice, fire-recall sentiment, 4xe lease MF/residuals, OTA updates | Yes | HIGH |
| **WranglerForum** | `wranglerforum.com` | All-generations depth: long-term reliability, wheeling, legacy knowledge. Use for **ownership depth**, JLWF for **buying** | Yes | HIGH |
| **Edmunds forums** | `forums.edmunds.com` (#74087) | Canonical crowd-sourced **monthly MF + residual** postings | Yes | HIGH |
| **Reddit** r/JeepWrangler, r/Jeep, r/4xe | reddit.com | Sentiment + frequency-of-complaint signal; weak on structured price/lease data | Yes | MEDIUM |
| **YouTube** | — | TrailRecon (overlanding, 4xe range tests), TFLcar/TFLoffroad (new-model + MY news), Dirt Lifestyle (builds), Jeep Informant. Feedspot "40 Jeep channels" as seed set | Yes | MEDIUM |
| **Discord / Facebook / IG-TikTok** | — | Social chatter migrated here, but **low mineable value** (small Discords ~74–298 members; FB closed/ephemeral; IG = inspiration not data) | Yes but low-signal | MEDIUM/LOW |

**Net:** casual chatter has diffused to Reddit/FB/Discord, but **ordering, pricing, lease MF/residual, and order-tracking still concentrate on the forums** — that's where the engine should mine HARD numbers.

### 3.2 What the community argues about that a generic framework misses

Tagged **H = hard/quantifiable (belongs in the model)** · **S = soft risk flag**.

- **Powertrain fork (3.6 V6 · 2.0T · 4xe)** — *the* central config decision. Community read: **3.6 V6 = simplest, deepest parts ecosystem, wheel-to-200k** (minor: plastic oil-filter-housing ~100k); **2.0T = quicker, no tick, but more failure points** (turbo coolant loop, extra e-water-pump); **4xe = risk-heavy right now** (see below). **[H as discrete config; S for reliability]** — HIGH
- **4xe economics restructured (2025+)** — federal credit gone → higher effective new cost + resale pressure; **leases diverge** because Stellantis routes a *manufacturer* $7,500 (not a tax credit) on some inventory. Buyers who bought pre-cut reportedly gained ~$3,750 equity. **[H — dollar-quantifiable]** — HIGH
- **4xe fire recall + class action** — expanded Nov 2025 to ~228k units; some fires *after* the earlier software fix; park-outside guidance; stalling/no-restart reports. **[S — major safety/reliability flag]** — HIGH
- **Death wobble** — still reported on 2024–25 **stock** units at low mileage; community root-cause = caster/track-bar/ball-joints/bearings; dealer damper "fix" seen as masking. **[S]** — HIGH
- **UConnect 5 gremlins** — black-screen/reboot, audio dropouts, GPS-lock, a bad 2024–25 OTA causing power loss/shutdowns; dealers told to await a Q1 2026 fix. **[S]** — HIGH
- **TPMS recall** — ~79k 2024–25 units: remote-start antenna cable pinches TPMS cable. **[H — discrete VIN/MY flag]** — HIGH
- **Sky One-Touch power-top leaks** — front-corner/door-gap leaks + hydraulic/electronic stalls; frequently optioned, frequently complained. **[S — option-specific]** — HIGH
- **Auto start-stop** — widely disliked; eliminators are themselves flaky. **[S]** — HIGH
- **Body style → trim availability → resale liquidity** — 4-door has wider buyer pool (faster sell); some 2026 trims are **4-door-only** (Sahara, Moab 392). **[H — config input + semi-quantifiable liquidity]** — HIGH
- **Manual transmission** — 2026 only with 3.6 V6; **required for the 4.88 axle option**; thin used market; likely "last-of" before 2027. **[S trending H — availability flag]** — HIGH (2026); MEDIUM (2027 drop)
- **National-delivery discount-dealer ordering** — factory-order via Mark Dodge/Granger ~7% below invoice + price protection + ~10–16 wk wait; a distinct scenario with quantifiable price delta vs local. **[H]** — HIGH
- **Mods ↔ warranty ↔ resale** — MMWA protects against blanket void, but lift/regear commonly costs *related* driveline claims; ESC/ride-height calibration is detectable; tasteful reversible mods help liquidity, heavy personalized builds hurt it. **[S — risk-by-mod-category]** — HIGH (warranty); MEDIUM (resale)
- **MY2026 vs 2027 timing** — 2027 brings a facelift, revived **Laredo**/**Sarge** editions, tech/ADAS upgrades, and expected **3.6 V6 → 3.0L twin-turbo Hurricane I6** re-power; 2027 production starts H2 2026. So 2026 = end-of-run + last easy V6/manual vs. refreshed pricier 2027. **[H — timing scenario]** — HIGH (facelift/lineup); MEDIUM (V6-drop timing)
- **Resale tailwind** — 2026 Wrangler again won the **ALG Residual Value Award** (best-in-class compact-SUV retention) — a quantifiable residual input to weigh against heavy-option/4xe depreciation. **[H]** — HIGH

---

## 4. Unknown unknowns — what wasn't publicly answerable

**Requires direct contact (no public source):**

| Question | Why unanswerable publicly | Who to contact | Stage |
|---|---|---|---|
| Actual out-the-door price from Koons/Criswell/Aventura for a specific 2026 config | Headline % is public; stacked OTD is quote-gated; 2023–24 tier %s need re-confirmation | Named order manager per dealer (forum group-buy threads) | On finalist config |
| Real insurance premium for the exact config + driver | Aggregators publish only modeled sample-driver averages; real premium needs ZIP + record + credit | Insurer / independent agent | Once per finalist |
| Extended-warranty (Mopar FlexCare) price | Quote-only (VIN + mileage); dealer-marked-up/negotiable | Dealer F&I / Mopar 833# | Finalist |
| GAP price | Quote-only (loan amount/LTV/lender); CU usually cheapest | Insurer rider / credit union / F&I | Finalist |
| Dealer mandatory add-ons & "market adjustment" | Not centrally published | Individual dealer OTD quote | Per-dealer |
| Mod **install labor** for target build | Parts retailers never list labor | Local 4x4 shop | On build change |
| Dealer cash / stair-step / VGP on slow trims | Manufacturer-to-dealer, never advertised (inferred from unusually deep discounts) | (Not directly obtainable) | — |
| Exact home-state + **county** use tax / annual ad-valorem for the user | Per-state, often per-county; user's state is a parameter not given | State DOR + county assessor | Once state known |
| PPI (pre-purchase inspection) findings on a specific used unit | Unit-specific | Independent Jeep/4x4 mechanic | Only if a used listing escalates |
| Exact MY the 3.6 V6 / manual is dropped | Not officially confirmed; press-reported | (Await Stellantis MY27 order guide) | Timing decision |
| VIN-level Manheim wholesale (MMR) | Dealer-only paid data | (Licensed dealer) | — |
| CR predicted-reliability detail | Paywalled | CR membership | If needed |

**Access frictions to design around (harness/collection):**
- **Edmunds, JLWranglerForums, Fuelly, and the FTC consumer page all return 403 to automated fetch** — plan for browser/manual collection or an authenticated path, not scripted GET.
- **TrueCar/CarsDirect/aggregator "invoice" pages** release the number only after capturing contact info (lead-gen gate).
- **No API** for: dealer pricing, state tax/titling, doc fees, mod parts, insurance quotes. Free structured APIs exist **only** for **EPA fueleconomy.gov** and **NHTSA** — lean on those.

---

## 5. Recommended collection cadence per source

| Cadence | Sources | Rationale |
|---|---|---|
| **One-time (per model year)** | Order guide PDFs / invoice-holdback spreadsheet; EPA fuel economy; Mopar maintenance schedule; factory warranty terms; iSeeCars depreciation; RepairPal/J.D. Power/CR reliability; CARB/emissions rules | Change only at MY rollover |
| **Monthly** | Jeep.com incentives; Edmunds + 4xeForums lease MF/residual threads; CarsDirect deals; KBB Fair Purchase Price + Cost-to-Own; Edmunds TMV; Manheim public index | Incentive/lease programs reset ~monthly; used values drift |
| **Weekly (during active decision window)** | CarGurus IMV/Deal Rating + days-on-lot; Jeep/dealer inventory & days-on-lot; forum deal threads | Listing-level and inventory move fast near a buy |
| **On-demand** | Mark Dodge / Granger / Koons / Criswell / Aventura quotes; NHTSA recall/complaint check on finalist config; mod parts pricing for target build; state DOR/DMV tax+titling for user's state; doc-fee lookup | Triggered by a finalist config, a surfaced listing, or a new recall |
| **Once per finalist (direct contact)** | Personalized insurance quote; extended-warranty quote; GAP quote; dealer OTD incl. add-ons; PPI (used only) | Quote-only; only worth the effort on shortlisted scenarios |
| **On rule change (event-driven)** | IRS clean-vehicle guidance; state EV credit (CO DOR/AFDC); state tax/doc-fee statutes | Statutory — watch, don't poll |

---

## 6. Handoff notes

- **Do before modeling:** re-scope class #12 (4xe federal credit → expired; state-only), add classes #18–21, and elevate national-delivery discount dealers to a sourcing-channel scenario.
- **Mod-parts verified:** Northridge4x4 / Quadratec / ExtremeTerrain confirmed live HIGH (Quadratec = 4xe-fitment authority, Northridge = per-component kit costing, ExtremeTerrain = only install-hours data); Morris4x4 is a 503-gated LOW cross-check. Install labor is quote-only everywhere.
- **Two free APIs to build on:** EPA fueleconomy.gov and NHTSA (both keyless JSON/XML). Everything else is HTML (some 403-gated) or quote-only.
- **Highest-trust structured feeds:** Jeep.com incentives (advertised, ZIP, monthly) · KBB Fair Purchase Price + Cost-to-Own · CarGurus IMV/Deal Rating · Edmunds lease megathread (MF+residual) · jlwranglerforums order-guide spreadsheet (invoice) · IRS.gov (credit status) · NHTSA (recalls).
- **Scope respected:** no data collected, no purchase/trim/config recommended, 4xe kept in-scope for discovery, target build treated as an unknown parameter.

*End of discovery report.*
