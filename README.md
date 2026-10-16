# Replication of Card & Krueger (1994) — "Minimum Wages and Employment"

A complete reproducibility package for the classic Card & Krueger (1994) paper
(*American Economic Review* 84(4), 772–793), which studies the effect of the
April 1992 New Jersey minimum-wage increase (from $4.25 to $5.05) on fast-food
employment, using Pennsylvania as a control group.

The package reproduces **Tables 2–4 and Figure 1** of the paper, produces
publication-style **three-line tables**, and adds an **independent extension**
that re-runs the difference-in-differences design on the non-employment margins
(prices, hours, workforce composition, and bonuses) through which firms may
absorb a higher minimum wage.

- **Language / environment:** Python 3.13
- **Data:** `01_DID/data/public.csv` — the Card–Krueger public-use restaurant
  survey (410 restaurants × 46 columns), included in this repository.

---

## Repository structure

```
6067project1/
├── 01_DID/                        # raw data and data documentation
│   ├── data/public.csv            #   survey data (410 stores)
│   ├── DATA_DICTIONARY.md         #   variable definitions
│   └── README.md                  #   data download / access notes
├── replicate_ck1994.py            # core replication: Tables 2–4 + Figure 1
├── make_three_line_tables.py      # publication-style three-line tables
├── independent_extension/         # independent extension (Direction 1)
│   ├── extension_did.py           #   DID on non-employment margins
│   └── extension_did_results.*    #   extension outputs
├── output/                        # generated tables and figures
│   ├── table2_updated.csv / .md
│   ├── table3_updated.csv / .md
│   ├── table4_updated.csv / .md
│   ├── figure1_updated.png
│   └── three_line_tables/         #   table2/3/4_three_line.png + .docx
├── Empirical_Report.docx          # the written report (final deliverable)
├── REPLICATION.md                 # replication notes and result comparison (中文)
├── 修改记录与差异说明.md             # fix log + data-version disclosure (中文)
├── requirements.txt               # pinned Python dependencies
├── run_all.py                     # one-command reproduction of all tables/figures
└── README.md                      # this file
```

---

## Requirements

Python 3.13 and the packages in `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

> `numpy==2.2.6` and `scipy==1.15.2` are pinned **exactly** because newer numpy
> releases fail with a DLL load error on Windows. All other packages are pinned
> to the versions used to produce the committed outputs.

---

## How to reproduce (one command)

```bash
cd 6067project1
pip install -r requirements.txt
python run_all.py
```

`run_all.py` runs the pipeline in dependency order and regenerates every main
table and figure:

1. **`replicate_ck1994.py`** — Tables 2–4 (CSV + Markdown) and Figure 1.
2. **`make_three_line_tables.py`** — the three-line tables (PNG + editable DOCX),
   read from the `table*_updated.csv` files produced in step 1.
3. **`independent_extension/extension_did.py`** — the independent extension DID.

The three scripts can also be run individually in that order.

---

## What each script does

### `replicate_ck1994.py`

The core replication. It builds the analysis variables exactly as in the paper
and produces Tables 2–4 and Figure 1 into `output/`.

| Step | Output |
| --- | --- |
| Table 2 | Means of selected outcome variables (store types, wave-1/wave-2 means) → `table2_updated.csv/.md` |
| Table 3 | Average employment before/after and the DID estimate → `table3_updated.csv/.md` |
| Table 4 | Reduced-form models for the change in employment → `table4_updated.csv/.md` |
| Figure 1 | Distribution of starting wage rates (Feb vs Nov 1992) → `figure1_updated.png` |

Key construction (matching the paper):

- FTE employment = `EMPFT + NMGRS + 0.5 × EMPPT` (managers = full-time).
- Wave-2 employment at **permanently closed** stores (`STATUS2 == 3`) is set to 0;
  **temporarily closed** stores (`STATUS2 ∈ {2,4,5}`) are treated as missing.
- The wage gap `GAP = (5.05 − WAGE_ST) / WAGE_ST` for NJ stores with
  `WAGE_ST < 5.05`, and 0 otherwise.

### `make_three_line_tables.py`

Turns the `table*_updated.csv` outputs into publication-style **three-line
tables** (top rule, header rule, bottom rule; no vertical/internal lines) as
PNG images and editable DOCX files in `output/three_line_tables/`.

### `independent_extension/extension_did.py`

The independent extension. It re-runs the DID design on the *non-employment*
adjustment margins — full-meal price, hours open, full-time share, recruiting
bonus, and cash registers — plus the starting wage (a manipulation check) and
FTE employment (a reference row). Outputs are `extension_did_results.csv/.md`
and a three-line table `extension_did_table.png/.docx`.

---

## Results vs. the original paper

The replication reproduces the paper's central results closely.

| Quantity | Replication | Paper |
| --- | --- | --- |
| DID (change in mean FTE, NJ − PA) | **2.75** (1.36) | 2.76 (1.36) |
| Table 4 model (i), NJ dummy | 2.33 (1.19) | 2.33 (1.19) |
| Table 4 model (ii), NJ dummy | 2.30 (1.20) | 2.30 (1.20) |
| Table 4 model (iii), wage gap | 15.65 (6.08) | 15.65 (6.08) |
| Table 4 model (iv), wage gap | 14.92 (6.21) | 14.92 (6.21) |
| Table 4 model (v), wage gap | 11.98 (7.42) | 11.91 (7.39) |
| Table 4 model (v), SER / p(controls) | 8.75 / 0.40 | 8.75 / 0.40 |
| Sample size (Table 4) | 357 | 357 |

All remaining differences are **small and data-driven**, not code errors: the
public-use `public.csv` differs marginally from the authors' original data. The
main ones are (1) the model (v) wage-gap coefficient (11.98 vs. 11.91, an
attenuation from (iv) to (v) of 0.803 vs. 0.798), and (2) the percentage of
full-time employees in Table 2 (28.6%/30.3% vs. 32.8%/35.9%), whose standard
errors nonetheless match. See `REPLICATION.md` and `修改记录与差异说明.md` for
the full disclosure, including the three coding errors that were identified and
fixed along the way (recruiting-bonus units, the paired-difference standard
errors with ρ = 0.45, and the omitted South-Jersey region dummy in model (v)).

### Independent extension (summary)

The DID on non-employment margins finds that the minimum-wage increase was
absorbed mainly through **higher prices** (a meal-price DID of 0.10, about a
20% pass-through of the wage increase) rather than through lower employment,
hours, bonuses, or capital. See the extension script and its outputs for the
full table.

---

## Data access

`public.csv` is the Card–Krueger (1994) **public-use** survey data and is
included in this repository. No access-restricted data are used by this
project. Variable definitions are in `01_DID/DATA_DICTIONARY.md`; the
download/access notes are in `01_DID/README.md`.

---

## Reproducibility notes

- All committed outputs were generated by the scripts above on Python 3.13 with
  the pinned dependencies in `requirements.txt`.
- `run_all.py` is the reusable workflow that regenerates the main tables and
  figures from raw data in one command.
- The commit history records meaningful stages of the work (data construction,
  each fix, three-line tables, the report, and the extension).
