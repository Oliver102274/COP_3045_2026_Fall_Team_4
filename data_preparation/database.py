"""Reusable SQLite source-table creation and read-only loading."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError

from .loading import load_csv_datasets
from .validation import REQUIRED_DATASETS, validate_required_datasets


def create_database(raw_data_dir: Path, database_path: Path) -> None:
    """Load sources before replacing tables and always release resources.

    A transaction is used, but SQLite table replacement is not guaranteed
    to restore previous tables after a later write failure.
    """
    datasets = load_csv_datasets(raw_data_dir)
    validate_required_datasets(datasets)
    database_path = Path(database_path).resolve()
    if not database_path.parent.is_dir():
        raise FileNotFoundError(f"Database output directory not found: {database_path.parent}")
    engine = create_engine(URL.create("sqlite", database=str(database_path)))
    table_name = None
    try:
        with engine.begin() as connection:
            for table_name in REQUIRED_DATASETS:
                datasets[table_name].to_sql(
                    table_name, connection, if_exists="replace", index=False
                )
    except (OSError, SQLAlchemyError) as error:
        context = f", table {table_name}" if table_name else ""
        raise RuntimeError(f"Cannot write database {database_path}{context}: {error}") from error
    finally:
        engine.dispose()


def read_source_tables(database_path: Path) -> dict[str, pd.DataFrame]:
    """Read five required tables without creating or modifying a database."""
    database_path = Path(database_path).resolve()
    if not database_path.is_file():
        raise FileNotFoundError(f"Database not found: {database_path}")
    url = URL.create(
        "sqlite", database=database_path.as_uri(),
        query={"mode": "ro", "uri": "true"},
    )
    engine = create_engine(url)
    table_name = None
    try:
        with engine.connect() as connection:
            available = inspect(connection).get_table_names()
            missing = [name for name in REQUIRED_DATASETS if name not in available]
            if missing:
                raise ValueError(f"Database {database_path} is missing required tables: {missing}")
            datasets = {}
            for table_name in REQUIRED_DATASETS:
                datasets[table_name] = pd.read_sql_table(table_name, connection)
        return datasets
    except (OSError, SQLAlchemyError) as error:
        context = f", table {table_name}" if table_name else ""
        raise RuntimeError(f"Cannot read database {database_path}{context}: {error}") from error
    finally:
        engine.dispose()
