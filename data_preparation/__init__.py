"""Reusable data loading and source validation without import-time file access."""

from .analytical import (
    build_analytical_dataset, calculate_skill_coverage, print_skill_coverage,
    summarize_skills, validate_job_preservation,
)
from .database import create_database, read_source_tables
from .loading import load_csv_datasets
from .validation import (
    validate_required_columns,
    validate_required_datasets,
    validate_unique_keys,
)

__all__ = [
    "build_analytical_dataset",
    "calculate_skill_coverage",
    "print_skill_coverage",
    "summarize_skills",
    "validate_job_preservation",
    "create_database",
    "read_source_tables",
    "load_csv_datasets",
    "validate_required_columns",
    "validate_required_datasets",
    "validate_unique_keys",
]
