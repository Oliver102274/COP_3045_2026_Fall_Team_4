"""Build job-level analytical data without changing the source tables."""

import pandas as pd

from .validation import (
    validate_required_columns, validate_required_datasets, validate_unique_keys,
)


def summarize_skills(jobs: pd.DataFrame, skills: pd.DataFrame) -> pd.DataFrame:
    """Combine sorted unique nonmissing names for exact matching job IDs."""
    validate_required_columns(jobs, "ai_jobs", ["job_id"])
    validate_required_columns(skills, "skills_demand", ["job_id", "skill"])
    matching = skills["job_id"].isin(jobs["job_id"])
    return (
        skills.loc[matching].dropna(subset=["skill"])
        .groupby("job_id", as_index=False)
        .agg(skills=("skill", lambda values: "; ".join(sorted(set(values)))))
    )


def calculate_skill_coverage(
    jobs: pd.DataFrame, skills: pd.DataFrame
) -> dict[str, int | float]:
    """Return unmatched rows/IDs, matched/unmatched jobs, total jobs, and coverage.

    coverage is a fraction from 0 to 1 (zero for no jobs). ID matches count
    even when skill names are missing; missing unmatched IDs are not distinct IDs.
    """
    validate_required_columns(jobs, "ai_jobs", ["job_id"])
    validate_required_columns(skills, "skills_demand", ["job_id"])
    unmatched = skills.loc[~skills["job_id"].isin(jobs["job_id"])]
    matched_jobs = int(jobs["job_id"].isin(skills["job_id"]).sum())
    total_jobs = len(jobs)
    return {
        "unmatched_skill_rows": len(unmatched),
        "distinct_unmatched_skill_ids": int(unmatched["job_id"].nunique()),
        "jobs_without_skills": total_jobs - matched_jobs,
        "matched_jobs": matched_jobs,
        "total_jobs": total_jobs,
        "coverage": matched_jobs / total_jobs if total_jobs else 0.0,
    }


def print_skill_coverage(metrics: dict[str, int | float]) -> None:
    """Print exact-ID coverage and its analytical limitation."""
    print(f"Unmatched skill rows: {metrics['unmatched_skill_rows']:,}")
    print(f"Distinct unmatched skill IDs: {metrics['distinct_unmatched_skill_ids']:,}")
    print(f"Jobs without matching skill records: {metrics['jobs_without_skills']:,}")
    print(
        f"Skill ID coverage: {metrics['matched_jobs']:,}/{metrics['total_jobs']:,} "
        f"jobs ({metrics['coverage']:.1%})"
    )
    print(
        "Missing skill matches do not mean no skills are required. "
        "Incomplete coverage limits skills analysis; job columns remain "
        "available for salary, experience, and remote-work comparisons."
    )


def validate_job_preservation(jobs: pd.DataFrame, result: pd.DataFrame) -> None:
    """Require every original job exactly once in the analytical result."""
    validate_required_columns(jobs, "ai_jobs", ["job_id"])
    validate_required_columns(result, "analytical dataset", ["job_id"])
    if (
        len(result) != len(jobs)
        or result["job_id"].isna().any()
        or result["job_id"].duplicated().any()
        or set(result["job_id"]) != set(jobs["job_id"])
    ):
        raise ValueError("The analytical dataset must retain every job exactly once.")


def build_analytical_dataset(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Validate and left join sources into one row per job without file access."""
    validate_required_datasets(datasets)
    required = {
        "ai_jobs": ["job_id", "job_title", "country", "posted_year"],
        "job_title_mapping": ["job_title"],
        "country_ai_trends": ["country", "year"],
        "skills_demand": ["job_id", "skill"],
    }
    for name, columns in required.items():
        validate_required_columns(datasets[name], name, columns)
    for name, keys in (
        ("ai_jobs", ["job_id"]),
        ("job_title_mapping", ["job_title"]),
        ("country_ai_trends", ["country", "year"]),
    ):
        validate_unique_keys(datasets[name], name, keys)

    jobs = datasets["ai_jobs"]
    trends = datasets["country_ai_trends"]
    result = jobs.merge(
        datasets["job_title_mapping"], on="job_title", how="left", validate="many_to_one"
    )
    trends = trends.rename(columns={
        "year": "posted_year",
        **{column: f"country_{column}" for column in trends.columns
           if column not in ["country", "year"]},
    })
    result = result.merge(
        trends, on=["country", "posted_year"], how="left", validate="many_to_one"
    )
    summary = summarize_skills(jobs, datasets["skills_demand"])
    result = result.merge(summary, on="job_id", how="left", validate="one_to_one")
    # data_dictionary remains reference-only; no derived values belong here.
    validate_job_preservation(jobs, result)
    return result
