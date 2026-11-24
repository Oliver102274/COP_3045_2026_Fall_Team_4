"""Create the source database through the reusable preparation package."""

from pathlib import Path
import sys


DATABASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DATABASE_DIR.parent
RAW_DATA_DIR = PROJECT_ROOT / "00_Raw_Data"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import create_database  # noqa: E402


def main() -> int:
    """Create the default database and report expected failures to the caller."""
    try:
        create_database(RAW_DATA_DIR, DATABASE_DIR / "project.db")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Database creation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
