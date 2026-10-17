# AI-Use Disclosure

This document records where and how AI assistance (Claude Code / Anthropic) was used in this replication of Card & Krueger (1994), how its output was checked, and the important AI errors or suggestions that I corrected or rejected. All substantive results, methodological choices, and the final wording of the written report are my own; AI was used as an assistant and does not substitute for my own verification and judgment.

## 1. Where and how AI was used

**Code.** AI wrote and iterated on the core replication script `replicate_ck1994.py` (Tables 2–4 and Figure 1), the three-line table generator `make_three_line_tables.py`, the independent-extension script `independent_extension/extension_did.py`, and the one-command workflow `run_all.py`.

**Variable construction.** AI drafted the analysis variables — FTE employment = `EMPFT + NMGRS + 0.5 × EMPPT`, the wage gap `GAP = (5.05 − WAGE_ST) / WAGE_ST`, and the treatment of permanently and temporarily closed stores — which I verified against the paper's description.

**Diagnostics and result comparison.** AI compared the computed results with the paper's Tables 2–4 and Figure 1, locating where the replication diverged from the published values.
**Writing.** AI drafted the documentation (`README.md`, `REPLICATION.md`, `修改记录与差异说明.md`, this disclosure) and early standalone drafts of report Sections 4 and 5, which I reviewed, revised, and integrated into the final report myself.

**Tables and figures.** AI generated all tables and figures (CSV / Markdown / PNG / DOCX), including the three-line tables.

## 2. How AI-generated code, analysis, and writing were checked

- Every reported number was compared line-by-line against the paper's tables, footnotes, and text.
- Regressions were re-run in `statsmodels` and the coefficients, standard errors, and t-statistics were cross-checked against the paper, not just visually inspected.
- Variable definitions and sample restrictions were verified against the paper's own description of the data.
- I read and edited the AI-drafted code and prose; the final report and the committed outputs are the versions I verified and approved.

## 3. Important AI errors or suggestions that you corrected or rejected

**Errors corrected**

1. **Four substantive errors in the first version of the replication code**, without which the tables and figures would have been wrong: (a) the recruiting-bonus variable was not scaled by 100; (b) the Table 3 standard errors did not use the paper's paired-difference formula (ρ = 0.45); (c) Table 4 model (v) omitted the South-Jersey region dummy `SOUTHJ`; (d) Figure 1 used incorrect histogram bins/midpoints (fixed to 14 groups with midpoints 4.25–5.55).
2. **Data-version disclosure.** The AI initially described the replication as "exact"; after verifying two minor differences (the Table 4 model (v) wage-gap coefficient 11.98 vs. 11.91, and the Table 2 full-time-employee shares), I corrected this to "near-exact" and added an honest disclosure that the public-use `public.csv` differs slightly from the authors' original data.
3. **Runtime error in the extension script.** `extension_did.py` raised `KeyError: 'nd'` (a column was referenced after being dropped); fixed before the extension results were generated.

For detailed revision logs, please refer to the 修改记录与差异说明.md document.



