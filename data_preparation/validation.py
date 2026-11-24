"""Validate source structure and keys without changing the supplied tables."""

from collections.abc import Mapping, Sequence

import pandas as pd


REQUIRED_DATASETS = (
    "ai_jobs", "country_ai_trends", "data_dictionary",
    "job_title_mapping", "skills_demand",
)


def validate_required_datasets(datasets: Mapping[str, object]) -> None:
    """Require all five source datasets, allowing additional datasets."""
    missing = [name for name in REQUIRED_DATASETS if name not in datasets]
    if missing:
        raise ValueError(f"Missing required datasets: {', '.join(missing)}")


def validate_required_columns(
    frame: pd.DataFrame, dataset_name: str, columns: Sequence[str]
) -> None:
    """Raise a descriptive error when a source lacks required columns."""
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required columns: {missing}")


def validate_unique_keys(
    frame: pd.DataFrame, dataset_name: str, keys: Sequence[str]
) -> None:
    """Require existing, non-null, unique keys, including composite keys."""
    validate_required_columns(frame, dataset_name, keys)
    key_columns = list(keys)
    if frame[key_columns].isna().any().any() or frame.duplicated(key_columns).any():
        raise ValueError(
            f"{dataset_name} must have non-null, unique keys: {key_columns}"
        )
