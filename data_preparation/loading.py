"""Load the source CSV files without cleaning or transforming their values."""

from pathlib import Path

import pandas as pd

from .validation import REQUIRED_DATASETS, validate_required_datasets


def load_csv_datasets(raw_data_dir: Path) -> dict[str, pd.DataFrame]:
    """Read sorted CSVs, requiring the five project sources and keeping extras.

    Use pandas' default parsing, matching the original collection script.
    File and parsing failures identify the affected path.
    """
    raw_data_dir = Path(raw_data_dir)
    if not raw_data_dir.is_dir():
        raise FileNotFoundError(f"Raw data directory not found: {raw_data_dir}")
    try:
        csv_files = sorted(raw_data_dir.glob("*.csv"))
    except OSError as error:
        raise OSError(f"Cannot list CSV files in {raw_data_dir}: {error}") from error

    sources = {path.stem: path for path in csv_files}
    missing = [f"{name}.csv" for name in REQUIRED_DATASETS if name not in sources]
    if missing:
        raise FileNotFoundError(
            f"Missing required CSV files in {raw_data_dir}: {', '.join(missing)}"
        )
    validate_required_datasets(sources)

    datasets = {}
    for name, path in sources.items():
        try:
            datasets[name] = pd.read_csv(path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError) as error:
            raise ValueError(f"Cannot parse CSV {path}: {error}") from error
        except OSError as error:
            raise OSError(f"Cannot read CSV {path}: {error}") from error
    return datasets
