"""Entry point for generating graphical EDA visualizations using the unified charts module."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "05-Report"
if str(REPORT_DIR) not in sys.path:
    sys.path.insert(0, str(REPORT_DIR))

from reporting.charts import generate_eda_charts  # noqa: E402


def load_data(csv_path: Path | None = None) -> pd.DataFrame:
    """Load the cleaned analytical dataset from CSV."""
    target_path = csv_path or (PROJECT_ROOT / "03_Data_Cleaning" / "clean_data.csv")
    if not target_path.is_file():
        raise FileNotFoundError(f"Cleaned dataset not found at: {target_path}")
    return pd.read_csv(target_path)


def main() -> int:
    """Parse arguments and generate the three EDA visualizations."""
    parser = argparse.ArgumentParser(description="Generate the project's EDA plots.")
    parser.add_argument(
        "--save-only",
        action="store_true",
        help="Save plots to 04_EDA/output without opening interactive windows.",
    )
    args = parser.parse_args()

    if args.save_only:
        plt.switch_backend("Agg")

    output_dir = Path(__file__).resolve().parent / "output"
    df = load_data()
    saved_paths = generate_eda_charts(df, output_dir)

    for path in saved_paths:
        print(f"Saved EDA chart: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())