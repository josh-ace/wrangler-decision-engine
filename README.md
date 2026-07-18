# Wrangler Decision Engine

Makes the true cost structure of a 2026 Jeep Wrangler purchase visible. The
deliverable is a multi-tab **`.xlsx` report** that decomposes the decision layer
by layer and sizes each price-affecting lever in dollars — transparency, not a
ranked recommendation. See [`spec.md`](spec.md) for the full framework.

This repo is the **engine**: the Python that produces and updates that `.xlsx`.

## Architecture

> **Python renders + refreshes. Excel formulas compute.**

Python is a data loader and renderer, *not* a runtime engine. Once the workbook
is rendered it is self-contained — every calculation lives as an Excel formula in
the file, and the user never needs Python to *use* the tool, only to refresh
market data.

| Layer | Owner | What it does |
|---|---|---|
| `Inputs`, `Notes` | **User** | Budget, horizon, HYSA rate, state, notes. Python never writes these. |
| `Data_*` | **Python** | Raw source data, one Excel Table per tab. Rewritten by `engine refresh`. |
| `Analysis_*` | **Excel** | Formulas compute from `Data_*` tables + `Inputs` named ranges. No Python. |
| `Ref_*` | Reference | `Ref_Provenance` (every value's source) and `Ref_Legend` (how to read it). |

Two disciplines make refresh safe (enforced from the first render):

- **Excel Tables** — all `Data_*` rows live in named Tables, so formulas use
  structured references (`Trims[MSRP]`) that survive row add/remove.
- **Named ranges** — single-cell inputs are named ranges (`Input_Horizon`), so
  Analysis formulas never hard-code `Inputs!$B$2`.

## Install

Requires Python ≥ 3.10. [uv](https://docs.astral.sh/uv/) is preferred:

```bash
uv venv
uv pip install -e ".[dev]"
```

pip fallback:

```bash
python -m venv .venv && source .venv/Scripts/activate   # .venv/bin/activate on Unix
pip install -e ".[dev]"
```

## Run

```bash
engine render                       # -> build/wrangler.xlsx
engine render -o path/to/out.xlsx   # custom output path
engine refresh build/wrangler.xlsx  # rewrite Data_* tabs in place, preserve everything else
pytest                              # run the test suite
ruff check .                        # lint (optional)
```

`render` builds a fresh workbook from scratch. `refresh` opens an existing one and
rewrites only the `Data_*` tabs from source data — user tabs, Analysis tabs, and
Ref tabs are left exactly as the user left them.

## Plug-in pattern for future ICs

The scaffold is a **walking skeleton**: every tab, table, and named range exists,
but the tables are empty and the Analysis tabs have no formulas yet. Each IC fills
in one module and the rest of the pipeline (render, refresh, tests) keeps working.

### To add real data to a `Data_*` tab

1. Edit the module in `src/engine/data/` (e.g. `trims.py`). Implement `load()` to
   return a list of rows, each matching `COLUMNS` (the renderer appends the
   `Source` / `As_Of_Date` provenance columns automatically). Nothing else changes
   — `render()` and refresh already lay the table down.
2. The unit test in `tests/test_data_modules.py` already asserts `load()` returns
   rows the width of `COLUMNS`; it starts passing with real data for free.
3. Extend `tests/test_e2e.py` with any content assertions specific to your data.

A *new* data tab: add one module in `src/engine/data/`, then append it to
`DATA_MODULES` in `src/engine/data/__init__.py`. The renderer, refresh, and the
E2E expected-tab list all pick it up automatically.

### To add formulas to an `Analysis_*` tab

1. Edit the module in `src/engine/analysis/` (e.g. `financing.py`). Implement
   `setup_formulas(ws)` to write the Excel formulas — reference `Data_*` tables via
   structured references (`Trims[MSRP]`) and inputs via named ranges
   (`Input_Horizon`). Formulas are Excel-native; Python only writes them.
2. The unit test in `tests/test_analysis_modules.py` calls `setup_formulas` on a
   blank sheet — extend it to assert the formulas you expect.

A *new* analysis tab: add one module, append it to `ANALYSIS_MODULES` in
`src/engine/analysis/__init__.py`.

### Where things live

```
src/engine/
  __init__.py        render_workbook() / refresh_workbook() — public API
  cli.py             `engine render` / `engine refresh`
  workbook.py        tab layout, user tabs, Ref tabs, named ranges
  xlsx.py            shared Excel-Table helpers (the table discipline)
  data/              one module per Data_* tab — load() + render()
  analysis/          one module per Analysis_* tab — setup_formulas()
  refresh/           refresh merge logic (Data_* tabs only)
tests/               unit test per module + E2E smoke + refresh-preservation
```

### The tests to keep green

- `pytest` must stay green with no skips after every IC.
- `tests/test_e2e.py::test_render_produces_all_tabs_tables_and_named_range` — the
  smoke test; asserts the full tab set, a Table per `Data_*` tab, and a named range.
- `tests/test_e2e.py::test_refresh_preserves_user_edits` — asserts a user edit on
  `Inputs` survives a refresh. Any change to refresh must keep this passing.
