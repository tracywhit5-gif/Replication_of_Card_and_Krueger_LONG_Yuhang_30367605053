"""
Independent Extension (Direction 1): DID on non-employment adjustment margins.

Card & Krueger (1994) report a difference-in-differences estimate only for FTE
employment. Economic theory says firms facing a higher minimum wage can absorb
the cost without cutting employment, via higher output prices, shorter hours,
substitution toward part-time workers, or reduced non-wage compensation. This
script re-runs the same DID design on each of those margins.

Estimator: balanced store-level change
    d_i    = y2_i - y1_i   (stores observed in both waves)
    DID    = mean(d | NJ) - mean(d | PA)
    SE(DID)= sqrt( SE(d|NJ)^2 + SE(d|PA)^2 )   (Welch, no equal-var assumption)
    t      = DID / SE(DID),  p = 2 * (1 - Phi(|t|))

All outputs are written into this folder (independent_extension/).
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "01_DID", "data", "public.csv")

# ---------------------------------------------------------------------------
# Load and construct outcomes
# ---------------------------------------------------------------------------
def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)

    # FTE employment with the paper's closure convention: permanent closure
    # (STATUS2 == 3) -> employment 0; temporarily closed (2/4/5) -> missing.
    df["fte1"] = df["EMPFT"] + df["NMGRS"] + 0.5 * df["EMPPT"]
    df["fte2"] = df["EMPFT2"] + df["NMGRS2"] + 0.5 * df["EMPPT2"]
    df.loc[df["STATUS2"] == 3, "fte2"] = 0.0
    df.loc[df["STATUS2"].isin([2, 4, 5]), "fte2"] = np.nan

    # Full meal price = soda + fries + entree (missing if any component missing).
    df["meal1"] = df["PSODA"] + df["PFRY"] + df["PENTREE"]
    df["meal2"] = df["PSODA2"] + df["PFRY2"] + df["PENTREE2"]

    # Full-time share of non-managerial workers (percentage).
    denom1 = df["EMPFT"] + df["EMPPT"]
    denom2 = df["EMPFT2"] + df["EMPPT2"]
    df["ftshare1"] = np.where(denom1 > 0, df["EMPFT"] / denom1 * 100, np.nan)
    df["ftshare2"] = np.where(denom2 > 0, df["EMPFT2"] / denom2 * 100, np.nan)

    # Recruiting bonus / special incentive (0/1 -> percentage).
    df["bonus1"] = df["BONUS"] * 100
    df["bonus2"] = df["SPECIAL2"] * 100

    return df


# Each outcome: (label, wave1 col, wave2 col, unit, decimals)
OUTCOMES = [
    ("Starting wage",        "WAGE_ST", "WAGE_ST2", "$",      2),
    ("FTE employment",       "fte1",    "fte2",     "workers", 2),
    ("Full meal price",      "meal1",   "meal2",    "$",      2),
    ("Hours open (weekday)", "HRSOPEN", "HRSOPEN2", "hrs",    2),
    ("Full-time share",      "ftshare1", "ftshare2", "%",     1),
    ("Recruiting bonus",     "bonus1",  "bonus2",    "%",      1),
    ("Cash registers",       "NREGS",   "NREGS2",    "units",  2),
]


def fmt(x: float, nd: int) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:.{nd}f}"


def stars(p: float) -> str:
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def did_one(df: pd.DataFrame, y1: str, y2: str, nd: int) -> dict:
    nj = df["STATE"] == 1
    pa = df["STATE"] == 0
    d = df[y2] - df[y1]

    d_nj = d[nj].dropna()
    d_pa = d[pa].dropna()

    chg_nj = float(d_nj.mean())
    chg_pa = float(d_pa.mean())
    se_nj = float(d_nj.std(ddof=1) / np.sqrt(len(d_nj)))
    se_pa = float(d_pa.std(ddof=1) / np.sqrt(len(d_pa)))

    did = chg_nj - chg_pa
    did_se = float(np.sqrt(se_nj ** 2 + se_pa ** 2))
    t = did / did_se
    p = float(2 * (1 - stats.norm.cdf(abs(t))))

    return dict(
        NJ_change=chg_nj, NJ_se=se_nj, N_NJ=len(d_nj),
        PA_change=chg_pa, PA_se=se_pa, N_PA=len(d_pa),
        DID=did, DID_se=did_se, t=t, p=p,
    )


# ---------------------------------------------------------------------------
# Three-line table rendering (PNG + DOCX)
# ---------------------------------------------------------------------------
def render_png(header, rows, col_widths, path):
    ncols = len(header)
    nbody = len(rows)
    total_w = sum(col_widths)
    header_h = 0.42
    body_h = 0.52
    fig_h = header_h + body_h * nbody + 0.25
    fig, ax = plt.subplots(figsize=(total_w, fig_h))
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    x = 0.0
    for j, w in enumerate(col_widths):
        # top rule (thick)
        ax.plot([0, total_w], [fig_h, fig_h], color="black", lw=1.5,
                solid_capstyle="butt")
        # header bottom rule (thin)
        ax.plot([0, total_w], [fig_h - header_h, fig_h - header_h],
                color="black", lw=0.75, solid_capstyle="butt")
        # bottom rule (thick)
        ax.plot([0, total_w], [fig_h - header_h - body_h * nbody,
                               fig_h - header_h - body_h * nbody],
                color="black", lw=1.5, solid_capstyle="butt")

    # header cells
    x = 0.0
    for j, (w, h) in enumerate(zip(col_widths, header)):
        ax.text(x + w / 2, fig_h - header_h / 2, h,
                ha="center", va="center", fontsize=9, fontweight="bold")
        x += w
    # body cells
    for i, row in enumerate(rows):
        y_top = fig_h - header_h - body_h * i
        x = 0.0
        for j, (w, cell) in enumerate(zip(col_widths, row)):
            ax.text(x + w / 2, y_top - body_h / 2, cell,
                    ha="center", va="center", fontsize=9, linespacing=1.25)
            x += w

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _set_borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.find(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders")
    if borders is None:
        borders = tcPr.makeelement(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders",
            {})
        tcPr.append(borders)
    for tag, spec in (("top", top), ("bottom", bottom)):
        el = borders.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + tag)
        if el is None:
            el = borders.makeelement(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}" + tag,
                {})
            borders.append(el)
        if spec is None:
            el.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val",
                   "nil")
        else:
            el.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val",
                   "single")
            el.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz",
                   str(spec))


def render_doc(header, rows, path):
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10)

    tbl = doc.add_table(rows=1 + len(rows), cols=len(header))
    tbl.alignment = 1  # center

    # header
    for j, h in enumerate(header):
        cell = tbl.rows[0].cells[j]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)
        _set_borders(cell, top=12, bottom=6)  # thick top, thin bottom

    # body
    for i, row in enumerate(rows):
        last = (i == len(rows) - 1)
        for j, txt in enumerate(row):
            cell = tbl.rows[i + 1].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for k, line in enumerate(str(txt).split("\n")):
                if k:
                    p = cell.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(line)
                run.font.size = Pt(9)
            _set_borders(cell, bottom=12 if last else None)

    doc.save(path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    df = load()

    results = []
    for label, y1, y2, unit, nd in OUTCOMES:
        r = did_one(df, y1, y2, nd)
        r["Outcome"] = label
        r["Unit"] = unit
        r["nd"] = nd
        results.append(r)

    tab = pd.DataFrame(results)[
        ["Outcome", "Unit", "nd", "NJ_change", "NJ_se", "PA_change", "PA_se",
         "DID", "DID_se", "t", "p", "N_NJ", "N_PA"]
    ]

    # Write CSV + Markdown (drop the internal decimal-width column)
    csv_path = os.path.join(BASE, "extension_did_results.csv")
    tab.drop(columns=["nd"]).to_csv(csv_path, index=False)

    md = tab.drop(columns=["nd"]).copy()
    for c in ["NJ_change", "NJ_se", "PA_change", "PA_se", "DID", "DID_se", "t"]:
        md[c] = md[c].map(lambda v: fmt(v, 2))
    md["p"] = md["p"].map(lambda v: f"{v:.3f}")
    md_path = os.path.join(BASE, "extension_did_results.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md.to_markdown(index=False))

    # Console summary
    print("Independent Extension -- DID on non-employment margins\n")
    print(f"{'Outcome':22s} {'NJ chg':>8s} {'PA chg':>8s} {'DID':>8s} "
          f"{'t':>6s} {'p':>6s}  {'N_NJ/N_PA'}")
    print("-" * 74)
    for _, r in tab.iterrows():
        nd = int(r["nd"])
        did_str = fmt(r["DID"], nd) + stars(r["p"])
        print(f"{r['Outcome']:22s} {fmt(r['NJ_change'], nd):>8s} "
              f"{fmt(r['PA_change'], nd):>8s} {did_str:>8s} "
              f"{fmt(r['t'], 2):>6s} {r['p']:>6.3f}  "
              f"{int(r['N_NJ'])}/{int(r['N_PA'])}")

    # Three-line table (PNG + DOCX)
    header = ["Outcome", "NJ change (SE)", "PA change (SE)", "DID (SE)", "t"]
    rows = []
    for _, r in tab.iterrows():
        nd = int(r["nd"])
        did_cell = f"{fmt(r['DID'], nd)}{stars(r['p'])}\n({fmt(r['DID_se'], nd)})"
        rows.append([
            r["Outcome"],
            f"{fmt(r['NJ_change'], nd)}\n({fmt(r['NJ_se'], nd)})",
            f"{fmt(r['PA_change'], nd)}\n({fmt(r['PA_se'], nd)})",
            did_cell,
            fmt(r["t"], 2),
        ])
    col_widths = [1.9, 1.5, 1.5, 1.5, 0.7]
    png_path = os.path.join(BASE, "extension_did_table.png")
    docx_path = os.path.join(BASE, "extension_did_table.docx")
    render_png(header, rows, col_widths, png_path)
    render_doc(header, rows, docx_path)

    # Pass-through: meal-price DID / starting-wage DID
    wage = tab[tab["Outcome"] == "Starting wage"].iloc[0]
    meal = tab[tab["Outcome"] == "Full meal price"].iloc[0]
    pass_through = meal["DID"] / wage["DID"] * 100
    print(f"\nPass-through (meal-price DID / starting-wage DID): "
          f"{pass_through:.1f}% of the wage increase passed into a full meal's price.")

    print(f"\n[ok] outputs -> {BASE}")
    print(f"  {os.path.basename(csv_path)}")
    print(f"  {os.path.basename(md_path)}")
    print(f"  {os.path.basename(png_path)}")
    print(f"  {os.path.basename(docx_path)}")


if __name__ == "__main__":
    main()
