"""
One-command reproduction of the Card & Krueger (1994) replication package.

Runs the pipeline in dependency order:

  1. replicate_ck1994.py                -> Tables 2-4 (CSV + Markdown) + Figure 1
  2. make_three_line_tables.py          -> publication-style three-line tables
                                            (PNG + editable DOCX)
  3. independent_extension/extension_did.py -> independent extension: DID on
                                            non-employment adjustment margins

Each script is self-contained and writes into its own output folder. Run from
anywhere with:  python run_all.py
"""

from __future__ import annotations

import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("replicate_ck1994.py",
     "Tables 2-4 + Figure 1 (updated)"),
    ("make_three_line_tables.py",
     "three-line tables (PNG + DOCX)"),
    (os.path.join("independent_extension", "extension_did.py"),
     "independent extension: DID on non-employment margins"),
]


def main() -> None:
    print("=" * 72)
    print("Card & Krueger (1994) replication — one-command reproduction")
    print("=" * 72)

    for i, (script, desc) in enumerate(STEPS, 1):
        path = os.path.join(BASE, script)
        print(f"\n[{i}/{len(STEPS)}] {desc}")
        print(f"        running: {script}")
        result = subprocess.run([sys.executable, path], cwd=BASE)
        if result.returncode != 0:
            print(f"\n[FAILED] {script} exited with code {result.returncode}",
                  file=sys.stderr)
            sys.exit(result.returncode)

    print("\n" + "=" * 72)
    print("All steps completed successfully.")
    print("  tables  -> output/table2_updated.csv, table3_updated.csv, "
          "table4_updated.csv (+ .md)")
    print("  figure  -> output/figure1_updated.png")
    print("  3-line  -> output/three_line_tables/*.png and *.docx")
    print("  ext.    -> independent_extension/extension_did_results.* "
          "and extension_did_table.*")
    print("=" * 72)


if __name__ == "__main__":
    main()
