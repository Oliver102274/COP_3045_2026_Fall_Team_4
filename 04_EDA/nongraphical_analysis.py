"""Run the non-graphical EDA stage through NonGraphicalAnalyzer."""

from pathlib import Path
import sys


ANALYSIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ANALYSIS_DIR.parent
INPUT_PATH = PROJECT_ROOT / "03_Data_Cleaning" / "clean_data.csv"
OUTPUT_DIR = ANALYSIS_DIR / "output"
for import_root in (PROJECT_ROOT, ANALYSIS_DIR):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from nongraphical import NonGraphicalAnalyzer  # noqa: E402


def main() -> int:
    """Analyze the cleaned CSV and return failure on expected input/output errors."""
    try:
        NonGraphicalAnalyzer(INPUT_PATH, OUTPUT_DIR).run()
    except (OSError, ValueError) as error:
        print(f"Non-graphical EDA failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
