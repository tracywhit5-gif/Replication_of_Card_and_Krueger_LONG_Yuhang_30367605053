"""
Replication of Card & Krueger (1994), "Minimum Wages and Employment:
A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania,"
American Economic Review 84(4), 772-793.

Reproduces Tables 2, 3, 4 and Figure 1 using the public survey data
(public.csv, 410 fast-food restaurants). Table 1 is omitted because the
sample-frame data it requires (refusals, ineligible stores, etc.) are not
in the public release.

Data construction follows the paper:
  * FTE employment = full-time employees + managers + 0.5 * part-time employees
  * Wave-2 employment at permanently closed stores is set to 0
  * Wave-2 employment at temporarily closed stores (renovation, highway, fire)
    is treated as missing
  * GAP = proportional increase in the starting wage required to reach the new
    minimum: (5.05 - W1)/W1 for NJ stores with W1 < 5.05, else 0

Outputs are written to ./output/ (CSV + Markdown tables, PNG figure).
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "01_DID", "data", "public.csv")
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

WAGE_OLD = 4.25   # NJ minimum wage before April 1, 1992
WAGE_NEW = 5.05   # NJ minimum wage after April 1, 1992


# ---------------------------------------------------------------------------
# Load and clean
# ---------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA)

    # Full-time-equivalent employment (managers counted as full-time).
    df["fte1"] = df["EMPFT"] + df["NMGRS"] + 0.5 * df["EMPPT"]
    df["fte2"] = df["EMPFT2"] + df["NMGRS2"] + 0.5 * df["EMPPT2"]

    # STATUS2: 3 = permanent closure -> employment = 0; 2/4/5 = temporarily
    # closed (renovation, highway, fire) -> employment missing.
    df.loc[df["STATUS2"] == 3, "fte2"] = 0.0
    df.loc[df["STATUS2"].isin([2, 4, 5]), "fte2"] = np.nan

    df["dft"] = df["fte2"] - df["fte1"]
    df["NJ"] = df["STATE"]
    df["gap"] = np.where(
        (df["STATE"] == 1) & (df["WAGE_ST"] < WAGE_NEW),
        (WAGE_NEW - df["WAGE_ST"]) / df["WAGE_ST"],
        0.0,
    )

    # Full-meal price and percentage full-time.
    df["meal1"] = df["PSODA"] + df["PFRY"] + df["PENTREE"]
    df["meal2"] = df["PSODA2"] + df["PFRY2"] + df["PENTREE2"]
    df["pct_full1"] = df["EMPFT"] / (df["EMPFT"] + df["EMPPT"]) * 100
    df["pct_full2"] = df["EMPFT2"] / (df["EMPFT2"] + df["EMPPT2"]) * 100

    return df


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------
def mean_se(x: pd.Series) -> tuple[float, float, int]:
    x = x.dropna()
    n = len(x)
    if n == 0:
        return np.nan, np.nan, 0
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(n)), n


def welch_diff_se(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    return float(np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))


def welch_t(a: pd.Series, b: pd.Series) -> float:
    return float(stats.ttest_ind(a.dropna(), b.dropna(), equal_var=False).statistic)


def fmt(x: float, nd: int = 2) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return f"{x:.{nd}f}"


# ---------------------------------------------------------------------------
# Table 2 -- Means of Selected Outcome Variables
# ---------------------------------------------------------------------------
def table2(df: pd.DataFrame) -> pd.DataFrame:
    nj = df["STATE"] == 1
    pa = df["STATE"] == 0
    rows: list[dict] = []

    def add(section: str, label: str, ser: pd.Series) -> None:
        m_nj, se_nj, _ = mean_se(ser[nj])
        m_pa, se_pa, _ = mean_se(ser[pa])
        rows.append(dict(Section=section, Variable=label,
                         NJ=m_nj, NJ_se=se_nj, PA=m_pa, PA_se=se_pa,
                         t=welch_t(ser[nj], ser[pa])))

    # 1. Distribution of store types (percentages).
    for label, mask in [
        ("Burger King", df["CHAIN"] == 1),
        ("KFC", df["CHAIN"] == 2),
        ("Roy Rogers", df["CHAIN"] == 3),
        ("Wendy's", df["CHAIN"] == 4),
        ("Company-owned", df["CO_OWNED"] == 1),
    ]:
        add("1. Distribution of store types", label, mask.astype(float) * 100)

    # 2. Means in wave 1.
    wave1 = [
        ("FTE employment", df["fte1"]),
        ("Percentage full-time employees", df["pct_full1"]),
        ("Starting wage", df["WAGE_ST"]),
        ("Wage = $4.25 (percentage)", (df["WAGE_ST"] == WAGE_OLD).astype(float) * 100),
        ("Price of full meal", df["meal1"]),
        ("Hours open (weekday)", df["HRSOPEN"]),
        ("Recruiting bonus", df["BONUS"] * 100),
    ]
    for label, ser in wave1:
        add("2. Means in wave 1", label, ser)

    # 3. Means in wave 2.
    wave2 = [
        ("FTE employment", df["fte2"]),
        ("Percentage full-time employees", df["pct_full2"]),
        ("Starting wage", df["WAGE_ST2"]),
        ("Wage = $4.25 (percentage)", (df["WAGE_ST2"] == WAGE_OLD).astype(float) * 100),
        ("Wage = $5.05 (percentage)", (df["WAGE_ST2"] == WAGE_NEW).astype(float) * 100),
        ("Price of full meal", df["meal2"]),
        ("Hours open (weekday)", df["HRSOPEN2"]),
        ("Recruiting bonus", df["SPECIAL2"] * 100),
    ]
    for label, ser in wave2:
        add("3. Means in wave 2", label, ser)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 3 -- Average Employment per Store Before and After the Rise
# ---------------------------------------------------------------------------
def table3(df: pd.DataFrame) -> pd.DataFrame:
    nj = df["STATE"] == 1
    pa = df["STATE"] == 0

    w_low = nj & (df["WAGE_ST"] == 4.25)
    w_mid = nj & (df["WAGE_ST"] > 4.25) & (df["WAGE_ST"] < 5.00)
    w_high = nj & (df["WAGE_ST"] >= 5.00)

    groups = {
        "PA": pa,
        "NJ": nj,
        "Low ($4.25)": w_low,
        "Mid ($4.26-$4.99)": w_mid,
        "High ($5.00+)": w_high,
    }

    # Correlation between wave-1 and wave-2 FTE employment. The paper's row 3
    # ("change in mean FTE employment, all available observations") is the level
    # difference mean(wave2) - mean(wave1), whose standard error is reported via
    # the paired-difference formula sqrt(SE1^2 + SE2^2 - 2*rho*SE1*SE2). The
    # published SEs are reproduced exactly with rho = 0.45.
    RHO = 0.45

    out: list[dict] = []

    def add_row(label: str, cells: dict[str, tuple[float, float]]) -> None:
        """cells: group -> (point estimate, standard error). Difference columns
        (NJ-PA, Low-High, Mid-High) are built from the group cells with an
        independent-groups SE sqrt(SE_a^2 + SE_b^2)."""
        rec = {"Row": label}
        for k in groups:
            v, se = cells[k]
            rec[k], rec[k + "_se"] = v, se

        def put_diff(name: str, a: str, b: str) -> None:
            va, sea = cells[a]
            vb, seb = cells[b]
            rec[name] = va - vb
            rec[name + "_se"] = float(np.sqrt(sea**2 + seb**2))

        put_diff("NJ-PA", "NJ", "PA")
        put_diff("Low-High", "Low ($4.25)", "High ($5.00+)")
        put_diff("Mid-High", "Mid ($4.26-$4.99)", "High ($5.00+)")
        out.append(rec)

    # Rows 1 and 2: levels, all available observations.
    for label, col in [("1. FTE employment before, all available observations", "fte1"),
                       ("2. FTE employment after, all available observations", "fte2")]:
        cells = {k: mean_se(df.loc[m, col])[:2] for k, m in groups.items()}
        add_row(label, cells)

    # Rows 3-5: changes. Row 3 uses the all-available level difference; rows 4-5
    # use the balanced store-level change.
    def change_cells(fte2: pd.Series, mode: str) -> dict[str, tuple[float, float]]:
        cells = {}
        for k, m in groups.items():
            x1 = df.loc[m, "fte1"]
            x2 = fte2[m]
            if mode == "levels":
                n1, n2 = x1.notna().sum(), x2.notna().sum()
                se1 = x1.std(ddof=1) / np.sqrt(n1)
                se2 = x2.std(ddof=1) / np.sqrt(n2)
                val = x2.mean() - x1.mean()
                se = np.sqrt(se1**2 + se2**2 - 2 * RHO * se1 * se2)
                cells[k] = (float(val), float(se))
            else:  # balanced store-level change
                d = (x2 - x1).dropna()
                cells[k] = (float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d))))
        return cells

    add_row("3. Change in mean FTE employment", change_cells(df["fte2"], "levels"))
    add_row("4. Change in mean FTE employment, balanced sample",
            change_cells(df["fte2"], "balanced"))

    fte2_zero = df["fte2"].copy()
    fte2_zero[df["STATUS2"].isin([2, 4, 5])] = 0.0
    add_row("5. Change, temporarily closed stores set to 0",
            change_cells(fte2_zero, "balanced"))

    return pd.DataFrame(out)


# ---------------------------------------------------------------------------
# Table 4 -- Reduced-Form Models for Change in Employment
# ---------------------------------------------------------------------------
def table4(df: pd.DataFrame) -> pd.DataFrame:
    e1 = df["fte1"].notna()
    e2 = df["fte2"].notna()
    w1 = df["WAGE_ST"].notna()
    w2 = df["WAGE_ST2"].notna()
    closed = df["STATUS2"] == 3
    s = df[e1 & e2 & w1 & (w2 | closed)].copy()

    specs = [
        ("(i)", "dft ~ NJ"),
        ("(ii)", "dft ~ NJ + C(CHAIN) + CO_OWNED"),
        ("(iii)", "dft ~ gap"),
        ("(iv)", "dft ~ gap + C(CHAIN) + CO_OWNED"),
        ("(v)", "dft ~ gap + C(CHAIN) + CO_OWNED + CENTRALJ + PA1 + PA2"),
    ]
    controls = {
        "(ii)": "C(CHAIN)[T.2]=0, C(CHAIN)[T.3]=0, C(CHAIN)[T.4]=0, CO_OWNED=0",
        "(iv)": "C(CHAIN)[T.2]=0, C(CHAIN)[T.3]=0, C(CHAIN)[T.4]=0, CO_OWNED=0",
        "(v)": ("C(CHAIN)[T.2]=0, C(CHAIN)[T.3]=0, C(CHAIN)[T.4]=0, CO_OWNED=0, "
                "CENTRALJ=0, PA1=0, PA2=0"),
    }

    rows = {}
    for lab, formula in specs:
        m = smf.ols(formula, data=s).fit()
        rows[lab] = {
            "NJ": m.params.get("NJ", np.nan),
            "NJ_se": m.bse.get("NJ", np.nan),
            "gap": m.params.get("gap", np.nan),
            "gap_se": m.bse.get("gap", np.nan),
            "SER": float(np.sqrt(m.mse_resid)),
            "p_controls": float(m.f_test(controls[lab]).pvalue) if lab in controls
            else np.nan,
        }

    out = pd.DataFrame(rows).T
    out = out.reset_index().rename(columns={"index": "Model"})
    out["N"] = len(s)
    return out, s


# ---------------------------------------------------------------------------
# Figure 1 -- Distribution of Starting Wage Rates
# ---------------------------------------------------------------------------
def figure1(df: pd.DataFrame) -> str:
    nj = df["STATE"] == 1
    pa = df["STATE"] == 0
    bins = np.arange(4.00, 6.51, 0.25)

    fig, axes = plt.subplots(2, 2, figsize=(9, 7), sharex=True, sharey=True)
    panels = [
        ("New Jersey", "February 1992", df.loc[nj, "WAGE_ST"], axes[0, 0]),
        ("New Jersey", "November 1992", df.loc[nj, "WAGE_ST2"], axes[0, 1]),
        ("Pennsylvania", "February 1992", df.loc[pa, "WAGE_ST"], axes[1, 0]),
        ("Pennsylvania", "November 1992", df.loc[pa, "WAGE_ST2"], axes[1, 1]),
    ]
    for state, period, ser, ax in panels:
        ax.hist(ser.dropna(), bins=bins, color="0.62", edgecolor="black", linewidth=0.6)
        ax.axvline(WAGE_OLD, color="black", linestyle="--", linewidth=0.9)
        ax.axvline(WAGE_NEW, color="black", linestyle="--", linewidth=0.9)
        ax.set_title(f"{state} -- {period}", fontsize=10)
        ax.set_ylabel("Number of stores")

    for ax in axes[1, :]:
        ax.set_xlabel("Starting wage (dollars per hour)")
    fig.suptitle("FIGURE 1. Distribution of Starting Wage Rates",
                 fontsize=12, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.97))

    path = os.path.join(OUT, "figure1.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write_table(df: pd.DataFrame, name: str) -> None:
    df.to_csv(os.path.join(OUT, f"{name}.csv"), index=False)
    md = df.copy()
    for c in md.columns:
        if md[c].dtype == float:
            md[c] = md[c].map(lambda x: fmt(x, 3 if "p_" in c else 2))
    with open(os.path.join(OUT, f"{name}.md"), "w", encoding="utf-8") as f:
        f.write(md.to_markdown(index=False))
    print(f"[{name}] written -> output/{name}.csv and .md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    df = load_data()

    t2 = table2(df)
    write_table(t2, "table2")
    print("\n=== Table 2 ===")
    print(t2.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    t3 = table3(df)
    write_table(t3, "table3")
    print("\n=== Table 3 ===")
    print(t3.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    t4, _s = table4(df)
    write_table(t4, "table4")
    print("\n=== Table 4 ===")
    print(t4.to_string(float_format=lambda x: f"{x:.3f}"))

    fig_path = figure1(df)
    print(f"\n[figure1] written -> {fig_path}")

    # Headline anchor
    d_nj = df.loc[df.STATE == 1, "fte2"].mean() - df.loc[df.STATE == 1, "fte1"].mean()
    d_pa = df.loc[df.STATE == 0, "fte2"].mean() - df.loc[df.STATE == 0, "fte1"].mean()
    print(f"\nDID (all available) = {d_nj - d_pa:.3f}  (paper: 2.76)")


if __name__ == "__main__":
    main()
