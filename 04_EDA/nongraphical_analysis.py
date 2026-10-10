from pathlib import Path

import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parent
INPUT_PATH = ANALYSIS_DIR.parent / "03_Data_Cleaning" / "clean_data.csv"
OUTPUT_DIR = ANALYSIS_DIR / "output"

EXPERIENCE_ORDER = ["Entry", "Mid", "Senior"]
REMOTE_ORDER = ["Remote", "Hybrid", "Onsite"]
NUMERIC_COLUMNS = [
    "salary_min_usd",
    "salary_max_usd",
    "salary_midpoint_usd",
    "min_experience_years",
    "posted_year",
    "country_total_ai_jobs",
    "country_avg_salary_usd",
    "country_remote_percentage",
]
CATEGORY_COLUMNS = [
    "experience_level",
    "remote_type",
    "country",
    "company_type",
    "company_size",
    "industry",
    "employment_type",
    "role_category",
    "posted_year",
]
GROUP_COLUMNS = [
    "experience_level",
    "remote_type",
    "country",
    "company_type",
    "company_size",
    "industry",
    "role_category",
    "posted_year",
]


def print_section(title):
    """Print a numbered-looking heading so console output stays scannable."""
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def ordered_category(series, order):
    """Keep a known label order and still retain unexpected labels."""
    present = [label for label in order if label in set(series.dropna())]
    extra = sorted(set(series.dropna()) - set(order))
    return pd.Categorical(series, categories=present + extra, ordered=True)


def salary_summary(df, column):
    """Job counts and salary/experience summaries for one categorical column."""
    summary = (
        df.groupby(column, dropna=False, observed=False)
        .agg(
            jobs=("job_id", "size"),
            jobs_with_salary=("salary_midpoint_usd", "count"),
            salary_midpoint_median=("salary_midpoint_usd", "median"),
            salary_midpoint_mean=("salary_midpoint_usd", "mean"),
            experience_years_median=("min_experience_years", "median"),
        )
        .reset_index()
    )
    summary.insert(0, "group", column)
    summary = summary.rename(columns={column: "level"})
    return summary


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)
    print_section("1. Read data")
    print(f"Source: {INPUT_PATH}")
    print(f"Jobs: {len(df):,} | Columns: {len(df.columns)}")

    df["salary_midpoint_usd"] = (df["salary_min_usd"] + df["salary_max_usd"]) / 2
    df["experience_level"] = ordered_category(df["experience_level"], EXPERIENCE_ORDER)
    df["remote_type"] = ordered_category(df["remote_type"], REMOTE_ORDER)
    skills = df["skills"].astype("string")
    df["has_matched_skills"] = skills.notna() & skills.str.strip().ne("")
    df["skills"] = skills

    print_section("2. Missing values")
    missing = df.isna().sum().rename("missing")
    missing_pct = (missing / len(df) * 100).round(2).rename("missing_pct")
    missing_table = pd.concat([missing, missing_pct], axis=1).reset_index(names="column")
    print(missing_table.to_string(index=False))

    print_section("3. Numeric summaries")
    numeric = df[NUMERIC_COLUMNS]
    numeric_summary = numeric.describe().T
    numeric_summary["missing"] = numeric.isna().sum()
    numeric_summary["skew"] = numeric.skew(numeric_only=True)
    numeric_summary = numeric_summary.reset_index(names="column")
    print(numeric_summary.round(2).to_string(index=False))
    print(
        "Salary midpoint uses only jobs with both bounds. "
        f"Jobs with a midpoint: {df['salary_midpoint_usd'].notna().sum():,} of {len(df):,}."
    )

    print_section("4. Category counts")
    category_frames = []
    for column in CATEGORY_COLUMNS:
        counts = (
            df[column]
            .value_counts(dropna=False)
            .rename_axis("level")
            .reset_index(name="jobs")
        )
        counts.insert(0, "column", column)
        counts["share_pct"] = (counts["jobs"] / len(df) * 100).round(2)
        category_frames.append(counts)
        print(f"\n{column}")
        print(counts.drop(columns="column").to_string(index=False))
    category_counts = pd.concat(category_frames, ignore_index=True)

    print_section("5. Salary and experience by group")
    grouped_salary = pd.concat(
        [salary_summary(df, column) for column in GROUP_COLUMNS],
        ignore_index=True,
    )
    for column in GROUP_COLUMNS:
        print(f"\n{column}")
        view = grouped_salary.loc[grouped_salary["group"] == column].drop(columns="group")
        print(view.round(2).to_string(index=False))

    print_section("6. Experience level by remote type")
    level_by_remote_counts = pd.crosstab(
        df["experience_level"], df["remote_type"], dropna=False, margins=True
    )
    level_by_remote_salary = pd.pivot_table(
        df,
        index="experience_level",
        columns="remote_type",
        values="salary_midpoint_usd",
        aggfunc="median",
        observed=False,
    )
    print("Job counts")
    print(level_by_remote_counts.to_string())
    print("\nMedian salary midpoint (USD)")
    print(level_by_remote_salary.round(2).to_string())

    print_section("7. Remote share by country")
    remote_share = (
        pd.crosstab(df["country"], df["remote_type"], normalize="index", dropna=False)
        .mul(100)
        .round(2)
    )
    remote_share["jobs"] = df.groupby("country", dropna=False).size()
    print(remote_share.to_string())

    print_section("8. Numeric correlations")
    correlation = df[NUMERIC_COLUMNS].corr(numeric_only=True).round(3)
    print(correlation.to_string())
    pair = df[["min_experience_years", "salary_midpoint_usd"]].dropna()
    print(
        "\nJobs used for experience-to-salary correlation: "
        f"{len(pair):,}. Coefficient: "
        f"{pair['min_experience_years'].corr(pair['salary_midpoint_usd']):.3f}."
    )
    country_pair = df[["salary_midpoint_usd", "country_avg_salary_usd"]].dropna()
    print(
        "Jobs used for job-midpoint to country-average correlation: "
        f"{len(country_pair):,}. Coefficient: "
        f"{country_pair['salary_midpoint_usd'].corr(country_pair['country_avg_salary_usd']):.3f}."
    )
    print(
        "country_avg_salary_usd and country_remote_percentage describe the "
        "country-year, not the individual job."
    )

    print_section("9. Matched skills")
    jobs_with_skills = int(df["has_matched_skills"].sum())
    print(f"Jobs with matched skills: {jobs_with_skills:,} of {len(df):,}.")
    print(
        "Most jobs have no skill match. Frequencies below describe matched jobs only "
        "and do not mean unmatched jobs require no skills."
    )
    skill_rows = (
        df.loc[df["has_matched_skills"], ["job_id", "skills"]]
        .assign(skill=lambda frame: frame["skills"].str.split(r"\s*;\s*"))
        .explode("skill")
    )
    skill_rows["skill"] = skill_rows["skill"].str.strip()
    skill_rows = skill_rows.loc[skill_rows["skill"].ne("") & skill_rows["skill"].notna()]
    skill_counts = (
        skill_rows.groupby("skill")["job_id"]
        .nunique()
        .sort_values(ascending=False)
        .rename("jobs")
        .reset_index()
    )
    if jobs_with_skills:
        skill_counts["share_of_matched_jobs_pct"] = (
            skill_counts["jobs"] / jobs_with_skills * 100
        ).round(2)
    else:
        skill_counts["share_of_matched_jobs_pct"] = pd.Series(dtype="float64")
    print(skill_counts.to_string(index=False))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing_table.to_csv(OUTPUT_DIR / "missing_values.csv", index=False)
    numeric_summary.to_csv(OUTPUT_DIR / "numeric_summary.csv", index=False)
    category_counts.to_csv(OUTPUT_DIR / "category_counts.csv", index=False)
    grouped_salary.to_csv(OUTPUT_DIR / "salary_by_group.csv", index=False)
    level_by_remote_counts.to_csv(OUTPUT_DIR / "experience_by_remote_counts.csv")
    level_by_remote_salary.to_csv(OUTPUT_DIR / "experience_by_remote_median_salary.csv")
    remote_share.to_csv(OUTPUT_DIR / "remote_share_by_country.csv")
    correlation.to_csv(OUTPUT_DIR / "numeric_correlation.csv")
    skill_counts.to_csv(OUTPUT_DIR / "skill_counts.csv", index=False)
    print_section("10. Saved tables")
    print(f"Summary tables written to: {OUTPUT_DIR}")
