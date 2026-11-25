"""Load source tables and export the validated job-level analytical dataset."""

from pathlib import Path
import sys

from pandas.errors import MergeError


DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "project.db"
PROJECT_ROOT = DATABASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import (  # noqa: E402
    build_analytical_dataset, calculate_skill_coverage,
    print_skill_coverage, read_source_tables,
)


def main() -> int:
    """Build and export analytical data, returning failure for expected errors."""
    output_path = DATABASE_DIR / "consolidated_data_database.csv"
    try:
        datasets = read_source_tables(DATABASE_PATH)
        df = build_analytical_dataset(datasets)
        metrics = calculate_skill_coverage(datasets["ai_jobs"], datasets["skills_demand"])
        print_skill_coverage(metrics)
        try:
            df.to_csv(output_path, index=False)
        except OSError as error:
            raise OSError(f"Cannot save analytical dataset to {output_path}: {error}") from error
    except (OSError, ValueError, RuntimeError, MergeError) as error:
        print(f"Analytical dataset creation failed: {error}", file=sys.stderr)
        return 1
    print(f"Analytical dataset: {len(df):,} rows, {len(df.columns)} columns")
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
