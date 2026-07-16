# Order Guide Parse — Notes, Ambiguities & Verification Pointers

**Source:** two 2026 Jeep Wrangler US "Customer Preferred Code Guide" PDFs in
`Ordering_Sheets/`.
**Publication dates (printed on every page):** ISSUED 2025-07-24, REISSUED
2025-08-06. `as_of_date` in the JSON is the **reissue** date `2025-08-06`.
**Extracted:** 2026-07-15.
**Method:** `pdftotext -layout` for orientation, then **pdfplumber word-coordinate
reconstruction** (script preserved in scratchpad as `dump.py` / `build_order_guide.py`)
because the multi-column trim tables interleave badly in plain text. All prices are
transcribed verbatim; no arithmetic was inferred except the cross-checks noted below.

---

## 1. Big-picture findings

- **No 4xe and no 392 in either guide.** The 2026 order guides cover only the 3.6L
  V6 (ERC) and 2.0L I4 turbo (EC1). The 4xe plug-in hybrid and 6.4L V8 (392) are
  **absent**. → For the engine/scenario space, **4xe is not applicable from this
  source.** (Corroborated by the standalone memory that federal EV credits expired
  2025-09-30, though that is a separate fact.) If 4xe/392 must be modeled, they need a
  different source (e.g., a separate 4xe order guide or Jeep.com).
- **Trims are `MODEL CODE` + `QUICK ORDER PACKAGE (QOP) CODE`.** Several "trims" share
  one model code: JLJL7x (Sport / Sport S / Willys), JLJS7x (Rubicon / Rubicon X).
  Sahara (JLJP74) and Sport RHD (JLUL74) are 4-door-only, each its own model code.
- **`trim.configurations[]` are fully-delivered prices** (base + engine/trans + QOP,
  **before destination**). Options/packages/colors are **extra-cost deltas** on top.
  This mirrors the guide's own note: "PRICE INCLUDES – BASE PRICE,
  ENGINE/TRANSMISSION AND QUICK ORDER PACKAGE … ADD DESTINATION CHARGE."

## 2. Powertrain code prefixes (verified by cross-checking price deltas)

| Prefix | Engine + Transmission | Notes |
|---|---|---|
| `23` | 3.6L V6 + 6-speed manual | Base/standard on Sport/Willys/Rubicon. Headline base MSRP is this config. **Marked "Late Availability."** |
| `22` | 2.0L I4 turbo + 8-speed auto | +$2,500 MSRP over base on Sport/Willys/Rubicon. Base engine on Sahara (22G) and Sport RHD (22A), where it is N/C. |
| `24` | 3.6L V6 + 8-speed auto | **4-door only.** +$4,500 over V6 manual on Sport family; +$2,000 over 2.0T base on Sahara (24G). Not offered on 2-door. |

- Verified: every `22-` price = its `23-` price + $2,500 (Sport family/Rubicon).
  Every `24-` = `23-` + $4,500. Sahara `24G` = `22G` + $2,000.
- **Engines are N/C; the automatic transmission is the priced item** in the powertrain
  table. Exception: on Sahara the V6 upgrade (24G) is priced +$2,000 because 2.0T is
  the Sahara base.

## 3. Trim base MSRP summary (before destination)

**2-door (JL):** Sport 33,785 · Sport S 38,035 · Willys 42,105 · Rubicon 44,765 ·
Rubicon X 54,715 (all at the base 23-/V6-manual config).
**4-door (JLU):** Sport 36,990 · Sport S 41,240 · Willys 45,310 · **Sahara 47,885**
(2.0T base) · Rubicon 49,270 · Rubicon X 59,220 · **Sport RHD 48,740** (2.0T).
Destination **$1,995** ($2,045 AK/HI) both body styles.

- **Rubicon X delta anomaly (explained, not an error):** the Rubicon X package costs
  **$9,950** on the manual (23-) but **$12,950** on the automatic (22-/24-) configs.
  Reason: the 22Y/24Y configs bundle the factory **35-inch tire package**, so the RubX
  package value is larger there. Both the Rubicon and Rubicon X delivered prices are
  transcribed verbatim, so scenario math is correct regardless. (Guide pages: JL 8, JLU 12.)

## 4. Package CONTENT — what's captured vs. approximate

- **Option-group contents** (ADA, ADH, AD3, AJ1, AJK, AJY, AEN, AGB, AYY, STJ, HT1,
  HT3, *VL, *NL) are enumerated from the **GROUP DETAIL** pages (JL 12-13, JLU 19-23)
  as `contents: [{code, description}]`.
- **Sport S / Willys QOP contents** come from the "PACKAGE CONTENT" X-mark grid on the
  model page (JL 2, JLU 2). Willys content is a superset of Sport S content in that grid.
- **Rubicon content** shown is the block highlighted on the Rubicon package-content page
  (JL 7, JLU 11) — treat as "notable standard equipment," not an exhaustive build sheet.
- **Rubicon X and Sahara base packages have NO line-item content list in the guide.**
  Their `package_content` is `null` with an explanatory `package_content_note`. Do not
  infer contents.
- **AGB "Xtreme 35 Tire Package" content differs slightly 2-door vs 4-door** (e.g.,
  2-door lists DHF Rock-Trac full-time 4WD + Dana M220 full-floating rear + Z5E 5650#
  GVW; 4-door lists BR4 perf brakes + Z1U 6250# GVW). Captured separately per body style.
- **AEN Dual Top** content: the guide splits HT1/HT3 and ST2/ST3 rows by drivetrain
  code (2TF/2TR/2TY etc.). Captured as the representative set (hard top + premium
  sunrider soft top + defroster/wiper/panel bag). The drivetrain-code conditionals were
  **not** modeled field-by-field.

## 5. Constraints captured (and their limits)

- `constraints.must_have` ← "M/H …"; `not_available_with` ← "N/A W/…";
  `only_one_of` ← "ONLY 1: …". These are transcribed from the option footnotes.
- **Per-trim option availability is coarse.** The guide encodes availability by which
  trim column shows an order code. I recorded `applies_to_trims` at the level of "which
  trim's options page the priced row appears on," and put finer conditions in `notes`.
  For strict legality checking, re-verify against the specific page.
- Some options appear with **different pricing by trim family** (Safety Group AJ1,
  Convenience Group AJK, Trailer Tow ADH). These are stored as **separate entries** with
  distinct `applies_to_trims` and a note — not merged — so no averaging is implied.

## 6. `invoice` is null everywhere (by scope)

The guides publish **FWP (Factory Wholesale Price)** and **MSRP** only. FWP is a
dealer/wholesale figure and is captured in its own `fwp` field, but it is **not** the
dealer "invoice," and **no invoice figure or approximation is provided.** Every
`invoice` field is `null`.

## 7. Things intentionally NOT fully transcribed

- **Full per-trim STANDARD EQUIPMENT lists** (JL pp. 14-17; JLU pp. 24-28). Long,
  non-priced. Page references retained here for later extraction if needed.
- **Sport RHD (JLUL74) options.** Only the base price ($48,740, 22A) is captured; it is
  a right-hand-drive fleet/mail variant. Its options pages (JLU 16-18) were not fully
  enumerated. Flagged in the trim's `package_content_note`.
- **Fleet-only telematics** (F2M Connect, Mobilisights data packages) are captured with
  full pricing under `fleet_only_options` but flagged — low relevance to a retail buy.
- **Color sales codes** were mapped to color names by y-coordinate alignment and
  spot-validated against known Jeep codes (PW7=Bright White, PX8=Black, PAU=Granite
  Crystal, PRC=Firecracker Red — all matched). The remaining code↔name pairs (e.g.,
  PJ5='41, PDS=Anvil) rely on the same alignment; low risk but not independently
  confirmed against an external code list.

## 8. Quick verification cross-checks (all passed)

- Sport-family: `22- = 23- + 2,500`, `24- = 23- + 4,500` for every trim. ✔
- Trim "PACKAGE VALUE PRICE" equals the delta between trim prices: Sport S = Sport +
  4,250; Willys = Sport + 8,320 (both body styles). ✔
- Rubicon X value: `RubX(23) − Rub(23) = 9,950`; `RubX(22/24) − Rub(22/24) = 12,950`. ✔
- Sahara: `24G − 22G = 2,000`. ✔
- Sample build re-computed from the JSON: JLU Rubicon 22R + destination + Steel Bumper
  Group (AD3) + Xtreme 35 (AGB) + Granite paint = 51,770 + 1,995 + 1,495 + 4,895 + 595
  = **$60,750**. ✔

## 9. Page-reference index (for re-verification)

| Content | JL 2-door | JLU 4-door |
|---|---|---|
| Cover / model index | 1 | 1 |
| Sport family base + powertrain + content | 2-3 | 2-3 |
| Sport family options | 4-5 | 4-5 |
| Sport family colors | 6 | 6 |
| Sahara base/options/colors | — | 7-10 |
| Rubicon base + content | 7-8 | 11-12 |
| Rubicon options | 9-10 | 13-14 |
| Rubicon colors | 11 | 15 |
| Sport RHD | — | 16-18 |
| GROUP DETAIL (package contents) | 12-13 | 19-23 |
| STANDARD EQUIPMENT | 14-17 | 24-28 |
