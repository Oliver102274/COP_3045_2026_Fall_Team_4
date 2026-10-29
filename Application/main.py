"""Run the complete project with the currently active Python/Conda environment."""

import os
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "05-Report" / "project_report.pdf"
STAGES = [
    ("Data collection", "01_Data_Collection/data_collection.py", []),
    ("Database creation", "02_Database/instantiate_database.py", []),
    ("Analytical dataset", "02_Database/create_analytical_dataset.py", []),
    ("Data cleaning", "03_Data_Cleaning/clean_data.py", []),
    ("Non-graphical EDA", "04_EDA/nongraphical_analysis.py", []),
    ("Graphical EDA", "04_EDA/eda_analysis.py", ["--save-only"]),
    ("PDF reporting", "05-Report/generate_report.py", []),
]


def main():
    """Execute every stage in order; stop immediately if a script fails."""
    environment = os.environ.copy()
    environment["MPLBACKEND"] = "Agg"
    for number, (name, script, arguments) in enumerate(STAGES, start=1):
        print(f"\n[{number}/{len(STAGES)}] {name}", flush=True)
        try:
            subprocess.run(
                [sys.executable, str(PROJECT_ROOT / script), *arguments],
                cwd=PROJECT_ROOT,
                env=environment,
                check=True,
            )
        except (subprocess.CalledProcessError, OSError) as error:
            print(f"ERROR: {name} failed: {error}", file=sys.stderr, flush=True)
            print("Workflow stopped. Any existing PDF may be from an earlier run.", file=sys.stderr)
            return 1

    if not REPORT_PATH.is_file() or REPORT_PATH.stat().st_size == 0:
        print(f"ERROR: No PDF report was generated at {REPORT_PATH}", file=sys.stderr)
        return 1
    print(f"\nWorkflow complete. PDF report: {REPORT_PATH}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
