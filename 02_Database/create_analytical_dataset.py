from pathlib import Path
import sys


DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "project.db"
PROJECT_ROOT = DATABASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import read_source_tables  # noqa: E402


if __name__ == "__main__":
    # Steps 1 and 2: Read source tables and close database resources.
    datasets = read_source_tables(DATABASE_PATH)
    ai_jobs_df = datasets["ai_jobs"]
    country_ai_trends_df = datasets["country_ai_trends"]
    data_dictionary_df = datasets["data_dictionary"]
    job_title_mapping_df = datasets["job_title_mapping"]
    skills_demand_df = datasets["skills_demand"]

    # Step 3: Create Analytical DataFrame.
    # Missing or repeated lookup keys could produce incorrect joins.
    for table_name, source_df, keys in [
        ("ai_jobs", ai_jobs_df, ["job_id"]),
        ("job_title_mapping", job_title_mapping_df, ["job_title"]),
        ("country_ai_trends", country_ai_trends_df, ["country", "year"]),
    ]:
        if source_df[keys].isna().any().any() or source_df.duplicated(keys).any():
            raise ValueError(
                f"{table_name} must have non-null, unique keys: {keys}"
            )

    # Many jobs can share the same title mapping.
    df = ai_jobs_df.merge(
        job_title_mapping_df,
        on="job_title",
        how="left",
        validate="many_to_one",
    )

    # Match the posting year and distinguish country statistics from
    # individual job attributes. Reuse the keys without duplicating them.
    country_ai_trends_df = country_ai_trends_df.rename(columns={
        "year": "posted_year",
        **{
            column: f"country_{column}"
            for column in country_ai_trends_df.columns
            if column not in ["country", "year"]
        },
    })
    df = df.merge(
        country_ai_trends_df,
        on=["country", "posted_year"],
        how="left",
        validate="many_to_one",
    )

    # Report exact ID matches without guessing corrections.
    matching_skill_rows = skills_demand_df["job_id"].isin(ai_jobs_df["job_id"])
    unmatched_skills_df = skills_demand_df.loc[~matching_skill_rows]
    jobs_with_skills = ai_jobs_df["job_id"].isin(skills_demand_df["job_id"])
    matched_jobs = int(jobs_with_skills.sum())
    total_jobs = len(ai_jobs_df)
    coverage = matched_jobs / total_jobs if total_jobs else 0.0

    print(f"Unmatched skill rows: {len(unmatched_skills_df):,}")
    print(f"Distinct unmatched skill IDs: {unmatched_skills_df['job_id'].nunique():,}")
    print(f"Jobs without matching skill records: {total_jobs - matched_jobs:,}")
    print(f"Skill ID coverage: {matched_jobs:,}/{total_jobs:,} jobs ({coverage:.1%})")
    print(
        "Missing skill matches do not mean no skills are required. "
        "Incomplete coverage limits skills analysis; job columns remain "
        "available for salary, experience, and remote-work comparisons."
    )

    # Summarize skills before joining so each job appears only once.
    # Drop missing names; a job with no usable names retains missing skills.
    skills_summary_df = (
        skills_demand_df.loc[matching_skill_rows]
        .dropna(subset=["skill"])
        .groupby("job_id", as_index=False)
        .agg(skills=("skill", lambda values: "; ".join(sorted(set(values)))))
    )
    df = df.merge(
        skills_summary_df,
        on="job_id",
        how="left",
        validate="one_to_one",
    )

    # data_dictionary_df documents columns and is not joined to jobs.
    # Preserve original job columns; derived calculations belong in EDA.
    if (
        len(df) != len(ai_jobs_df)
        or df["job_id"].isna().any()
        or df["job_id"].duplicated().any()
        or set(df["job_id"]) != set(ai_jobs_df["job_id"])
    ):
        raise ValueError("The analytical dataset must retain every job exactly once.")

    output_path = DATABASE_DIR / "consolidated_data_database.csv"
    df.to_csv(output_path, index=False)
    print(f"Analytical dataset: {len(df):,} rows, {len(df.columns)} columns")
    print(f"Saved to: {output_path}")
