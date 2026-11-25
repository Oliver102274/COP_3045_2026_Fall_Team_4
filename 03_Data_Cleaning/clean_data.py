"""Run the existing cleaning workflow through DataCleaner."""

from pathlib import Path
import sys


CLEANING_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CLEANING_DIR.parent
INPUT_PATH = PROJECT_ROOT / "02_Database" / "consolidated_data_database.csv"
OUTPUT_PATH = CLEANING_DIR / "clean_data.csv"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import DataCleaner  # noqa: E402


def main() -> int:
    """Clean the analytical CSV and return failure on expected input/output errors."""
    try:
        DataCleaner(INPUT_PATH, OUTPUT_PATH).run()
    except (OSError, ValueError) as error:
        print(f"Data cleaning failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
