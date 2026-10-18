---
name: ck1994-reproduce
description: Regenerate the Card & Krueger (1994) replication — Tables 2–4, Figure 1, the publication-style three-line tables, and the independent-extension DID — and verify the reproduced numbers against the paper.
---

# Card & Krueger (1994) — reproduction workflow

Use this skill to regenerate every main table and figure of the Card & Krueger
(1994) replication from the raw data, and to check the reproduced numbers
against the published paper.

Run everything from the project root (the directory containing `run_all.py`).

## Prerequisites

- Python 3.13
- `pip install -r requirements.txt`
  - `numpy==2.2.6` and `scipy==1.15.2` are pinned **exactly**; newer numpy fails
    with a DLL load error on Windows.

## One-command reproduction

```bash
python run_all.py
```

`run_all.py` runs the pipeline in dependency order:

1. `replicate_ck1994.py` — Tables 2–4 (CSV + Markdown) and Figure 1.
2. `make_three_line_tables.py` — publication-style three-line tables (PNG + editable DOCX).
3. `independent_extension/extension_did.py` — DID on the non-employment adjustment margins.

## Verify against the paper

After running, confirm these key numbers:

| Quantity | Reproduced | Paper |
| --- | --- | --- |
| DID (Δ mean FTE, NJ − PA) | 2.75 (1.36) | 2.76 (1.36) |
| Table 4 model (i), NJ dummy | 2.33 (1.19) | 2.33 (1.19) |
| Table 4 model (ii), NJ dummy | 2.30 (1.20) | 2.30 (1.20) |
| Table 4 model (iii), wage gap | 15.65 (6.08) | 15.65 (6.08) |
| Table 4 model (iv), wage gap | 14.92 (6.21) | 14.92 (6.21) |
| Table 4 model (v), wage gap | 11.98 (7.42) | 11.91 (7.39) |
| Table 4 sample size | 357 | 357 |

The two remaining small differences (the model (v) wage-gap coefficient and the
Table 2 full-time-employee shares) are documented data-version differences, not
code errors — see `REPLICATION.md` and `修改记录与差异说明.md`.

## Key variable construction (for auditing)

- FTE employment = `EMPFT + NMGRS + 0.5 × EMPPT`.
- Wave-2 FTE is 0 for permanently closed stores (`STATUS2 == 3`) and missing for
  temporarily closed stores (`STATUS2 ∈ {2,4,5}`).
- Wage gap `GAP = (5.05 − WAGE_ST) / WAGE_ST` for NJ stores with `WAGE_ST < 5.05`,
  else 0.

## Outputs

- `output/table2_updated.csv/.md`, `table3_updated.csv/.md`, `table4_updated.csv/.md`
- `output/figure1_updated.png`
- `output/three_line_tables/table2_three_line.png/.docx`, `table3_three_line.png/.docx`, `table4_three_line.png/.docx`
- `independent_extension/extension_did_results.csv/.md` and `extension_did_table.png/.docx`
