"""Load and validate report data, then calculate the original report results."""

from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_complex_dtype, is_numeric_dtype


NUMERIC_COLUMNS = (
    "min_experience_years", "salary_min_usd", "salary_max_usd", "posted_year",
)
REQUIRED_COLUMNS = (
    *NUMERIC_COLUMNS, "country", "standardized_title", "experience_level",
    "remote_type", "skills",
)


class DatasetSummary(TypedDict):
    """Named results passed to the PDF writer without changing the dataset."""

    row_count: int
    column_count: int
    first_year: float
    last_year: float
    country_count: int
    title_count: int
    experience_level_count: int
    remote_type_count: int
    summary_statistics: pd.DataFrame


class ReportFindings(TypedDict):
    """Named results passed to the PDF writer without changing the dataset."""

    most_frequent_title_count: int
    most_frequent_titles_text: str
    highest_mean_salary: float
    highest_salary_levels_text: str
    most_common_remote_count: int
    most_common_remote_types_text: str
    remote_percentage: float
    year_highest_count: int
    highest_posting_years_text: str
    skills_count: int
    skills_percentage: float


def validate_data(df: pd.DataFrame) -> None:
    """Reject unusable report input without cleaning or replacing any values."""
    if df.empty:
        raise ValueError("The reporting dataset is empty; provide rows of cleaned data.")
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Reporting dataset is missing required columns: {', '.join(missing)}")
    for column in NUMERIC_COLUMNS:
        values = df[column]
        if (
            not is_numeric_dtype(values)
            or is_bool_dtype(values)
            or is_complex_dtype(values)
        ):
            raise ValueError(f"Column '{column}' must contain numeric values or missing values.")
        present = values.dropna()
        if present.empty:
            raise ValueError(f"Column '{column}' has no numeric values for reporting.")
        if not np.isfinite(present).all():
            raise ValueError(f"Column '{column}' contains infinite values; review the cleaned data.")
    if df["standardized_title"].dropna().empty:
        raise ValueError("No standardized titles are available for the title chart and findings.")
    remote = df["remote_type"].dropna()
    if remote[remote.astype(str).str.strip() != ""].empty:
        raise ValueError("No nonblank work arrangements are available for reporting.")
    if df.dropna(subset=["experience_level", "salary_max_usd"]).empty:
        raise ValueError("No experience levels have an upper salary bound for reporting.")


def load_data(data_file: Path) -> pd.DataFrame:
    """Read a cleaned CSV and validate it before creating reporting outputs."""
    if not data_file.is_file():
        raise FileNotFoundError(f"Reporting input CSV not found: {data_file}")
    try:
        df = pd.read_csv(data_file)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"Reporting input CSV is empty: {data_file}") from error
    except (OSError, UnicodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Could not read reporting input CSV '{data_file}': {error}") from error
    validate_data(df)
    return df


def calculate_summary(df: pd.DataFrame) -> DatasetSummary:
    """Calculate dataset counts and statistics from a validated DataFrame."""
    row_count = len(df)
    column_count = len(df.columns)
    years = df["posted_year"].dropna().sort_values()
    first_year = years.min()
    last_year = years.max()
    country_count = df["country"].nunique()
    title_count = df["standardized_title"].nunique()
    experience_level_count = df["experience_level"].nunique()
    remote_type_count = df["remote_type"].nunique()

    summary_statistics = df[
        ["min_experience_years", "salary_min_usd", "salary_max_usd"]
    ].agg(["mean", "min", "median", "max"]).T
    return {
        "row_count": row_count,
        "column_count": column_count,
        "first_year": first_year,
        "last_year": last_year,
        "country_count": country_count,
        "title_count": title_count,
        "experience_level_count": experience_level_count,
        "remote_type_count": remote_type_count,
        "summary_statistics": summary_statistics,
    }


def calculate_findings(df: pd.DataFrame) -> ReportFindings:
    """Calculate the original findings, preserving ties and missing-value rules."""
    row_count = len(df)
    title_counts = df["standardized_title"].value_counts().sort_values(ascending=True)
    remote_arrangements = df["remote_type"].dropna()
    remote_arrangements = remote_arrangements[
        remote_arrangements.astype(str).str.strip() != ""
    ]
    remote_counts = remote_arrangements.value_counts().sort_values(ascending=True)
    year_counts = df.groupby("posted_year").size().sort_index()
    most_frequent_title_count = title_counts.max()
    most_frequent_titles = title_counts[
        title_counts == most_frequent_title_count
    ].index.tolist()
    most_frequent_titles_text = ", ".join(str(title) for title in most_frequent_titles)

    salary_by_experience = (
        df.dropna(subset=["experience_level", "salary_max_usd"])
        .groupby("experience_level")["salary_max_usd"]
        .mean()
    )
    highest_mean_salary = salary_by_experience.max()
    highest_salary_levels = salary_by_experience[
        salary_by_experience == highest_mean_salary
    ].index.tolist()
    highest_salary_levels_text = ", ".join(
        str(level) for level in highest_salary_levels
    )

    most_common_remote_count = remote_counts.max()
    most_common_remote_types = remote_counts[
        remote_counts == most_common_remote_count
    ].index.tolist()
    most_common_remote_types_text = ", ".join(
        str(remote_type) for remote_type in most_common_remote_types
    )
    remote_percentage = most_common_remote_count / len(remote_arrangements) * 100

    year_highest_count = year_counts.max()
    highest_posting_years = year_counts[
        year_counts == year_highest_count
    ].index.tolist()
    highest_posting_years_text = ", ".join(
        str(year) for year in highest_posting_years
    )

    skills_nonblank = df["skills"].notna() & (df["skills"].astype(str).str.strip() != "")
    skills_count = int(skills_nonblank.sum())
    skills_percentage = skills_count / row_count * 100
    return {
        "most_frequent_title_count": most_frequent_title_count,
        "most_frequent_titles_text": most_frequent_titles_text,
        "highest_mean_salary": highest_mean_salary,
        "highest_salary_levels_text": highest_salary_levels_text,
        "most_common_remote_count": most_common_remote_count,
        "most_common_remote_types_text": most_common_remote_types_text,
        "remote_percentage": remote_percentage,
        "year_highest_count": year_highest_count,
        "highest_posting_years_text": highest_posting_years_text,
        "skills_count": skills_count,
        "skills_percentage": skills_percentage,
    }
