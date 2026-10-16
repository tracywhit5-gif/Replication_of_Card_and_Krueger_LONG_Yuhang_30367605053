"""
Generate a standalone Word document containing only Section 5
("Independent Extension"), reporting the DID-on-adjustment-margins extension.

The replicated three-line table is embedded directly from this folder
(extension_did_table.png). The existing Empirical_Report.docx is not modified.
"""

from __future__ import annotations

import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(BASE, "Section5_Independent_Extension.docx")
TABLE_PNG = os.path.join(BASE, "extension_did_table.png")


def _font(run, size=11, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    _font(p.add_run(text), size=13, bold=True)


def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    _font(p.add_run(text), size=11.5, bold=True)


def para(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    _font(p.add_run(text))
    return p


def table_image(doc, path, width_in, caption_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    run = p.add_run()
    run.add_picture(path, width=Inches(width_in))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(10)
    _font(c.add_run(caption_text), size=9, italic=True)


def main():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    h1(doc, "5. Independent Extension")

    # ---------------------------------------------------------------- motivation
    para(doc,
         "The paper's central claim concerns employment, but the economic "
         "question it poses is broader. When a binding minimum wage raises the "
         "cost of low-skill labor, firms can respond along several margins: "
         "higher output prices, shorter operating hours, a shift in the "
         "full-time/part-time mix, lower non-wage compensation, or fewer stores. "
         "The paper reports the means of these variables (Table 2) but never "
         "takes them through the difference-in-differences design. This "
         "extension closes that gap: it re-runs the paper's difference-in-"
         "differences design on each non-employment margin, using the same "
         "survey and the same natural experiment, to ask through which channel "
         "the 1992 New Jersey minimum-wage increase was absorbed.")

    # ---------------------------------------------------------------- design
    h2(doc, "5.1 Design and method")
    para(doc,
         "I use the same 410-store sample and the same two waves as the paper. "
         "For each outcome I compute the balanced store-level change "
         "d_i = y_{i2} - y_{i1} for stores observed in both waves, and estimate "
         "the difference-in-differences as the difference between the New "
         "Jersey and Pennsylvania mean changes, with a Welch standard error "
         "(no equal-variance assumption). Seven outcomes are considered: the "
         "starting wage (a manipulation check that the design captures the "
         "treatment), FTE employment (a reference row that should reproduce the "
         "paper's Table 3), and five adjustment margins — the price of a full "
         "meal, weekday hours open, the full-time share of non-managerial "
         "workers, the recruiting bonus, and the number of cash registers (a "
         "capital stock that should not respond within eight months and "
         "therefore serves as a falsification test).")

    # ---------------------------------------------------------------- results
    h2(doc, "5.2 Results")
    para(doc,
         "Table 5 reports the results. The manipulation check passes: the New "
         "Jersey starting wage rose by 0.47 relative to Pennsylvania, a "
         "difference-in-differences of 0.50 (t = 9.75), confirming that the "
         "design captures the treatment. The FTE reference row reproduces the "
         "paper's balanced-sample estimate of 2.75 (SE 1.34). Among the "
         "adjustment margins, the only statistically significant response is "
         "the price of a full meal: the difference-in-differences is 0.10 "
         "(t = 2.29), i.e. New Jersey meal prices rose by about ten cents "
         "relative to Pennsylvania. Hours open (−0.11, t = −1.08), the "
         "recruiting bonus (2.37, t = 0.34), and the number of cash registers "
         "(−0.17, t = −1.61) all show no significant change. The full-time "
         "share rose by 7.8 percentage points in New Jersey relative to "
         "Pennsylvania, marginally significant (t = 1.83).")
    table_image(doc, TABLE_PNG, 6.3,
                "Table 5. Difference-in-differences estimates for non-employment "
                "adjustment margins.")
    para(doc,
         "Notes: standard errors in parentheses. *** p < 0.01, ** p < 0.05, "
         "* p < 0.1. Estimates use the balanced store-level change; the FTE row "
         "applies the paper's closure convention (permanent closure set to zero, "
         "temporary closure treated as missing).")

    # ---------------------------------------------------------------- interpretation
    h2(doc, "5.3 Interpretation")
    para(doc,
         "The results imply that the minimum-wage increase was absorbed "
         "primarily through higher prices rather than through lower employment. "
         "The meal-price difference-in-differences implies a pass-through of "
         "about 20 percent of the increase in the starting wage into the price "
         "of a full meal, consistent with a fast-food industry facing inelastic "
         "demand and passing a meaningful share of cost increases on to "
         "consumers. There is no evidence of adjustment along the hours, bonus, "
         "or capital margins: stores did not shorten hours, cut hiring "
         "incentives, or shed equipment. The composition result is notable: "
         "rather than substituting part-time for full-time workers, New Jersey "
         "stores moved slightly toward full-time staffing relative to "
         "Pennsylvania, though the estimate is only marginally significant and "
         "should be read cautiously.")
    para(doc,
         "Two caveats apply. First, the recruiting bonus is measured by two "
         "different survey items across waves (BONUS in wave 1, SPECIAL2 in "
         "wave 2), so that margin is the least directly comparable. Second, the "
         "balanced-sample design drops temporarily closed stores, so the FTE "
         "row (a New Jersey change of 0.47) differs slightly from the paper's "
         "all-available figure (0.59) but matches the paper's balanced-sample "
         "difference-in-differences exactly. On the whole, the extension "
         "reinforces the paper's central conclusion: the New Jersey minimum-wage "
         "increase did not reduce employment, and the cost was passed through "
         "mainly to prices.")

    doc.save(REPORT)
    print(f"[ok] section 5 written -> {REPORT}")


if __name__ == "__main__":
    main()
