"""Generate a data-drift report: current vs reference.

Evidently compares each feature's distribution in 'current' against 'reference'
and flags drift with statistical tests (KS for numerical, etc.). The output is
an HTML report you can open, plus a programmatic result you could alert on.
"""
import pandas as pd
from pathlib import Path
from evidently import Report
from evidently.presets import DataDriftPreset

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "monitoring" / "data"


def main():
    reference = pd.read_parquet(DATA / "reference.parquet")
    current = pd.read_parquet(DATA / "current.parquet")

    report = Report(metrics=[DataDriftPreset()])
    my_eval = report.run(current, reference)     # note: (current, reference) order
    my_eval.save_html(str(ROOT / "monitoring" / "drift_report.html"))
    print("saved drift_report.html")


if __name__ == "__main__":
    main()
