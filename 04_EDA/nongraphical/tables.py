"""Calculate descriptive tables from the cleaned dataset.

Every function takes a DataFrame and returns a new table. Nothing here prints,
reads files, or writes files, so the calculations can be reused by other stages.
"""

from collections.abc import Sequence

import pandas as pd

from data_preparation.validation import validate_required_columns


EXPERIENCE_ORDER = ("Entry", "Mid", "Senior")
REMOTE_ORDER = ("Remote", "Hybrid", "Onsite")
MIDPOINT_COLUMN = "salary_midpoint_usd"
NUMERIC_COLUMNS = (
    "salary_min_usd",
    "salary_max_usd",
    MIDPOINT_COLUMN,
    "min_experience_years",
    "posted_year",
    "country_total_ai_jobs",
    "country_avg_salary_usd",
    "country_remote_percentage",
)
CATEGORY_COLUMNS = (
    "experience_level",
    "remote_type",
    "country",
    "company_type",
    "company_size",
    "industry",
    "employment_type",
    "role_category",
    "posted_year",
)
# Every posting in the current data is full-time, so employment type is counted
# but not used to compare salaries between groups.
GROUP_COLUMNS = tuple(
    column for column in CATEGORY_COLUMNS if column != "employment_type"
)
# The midpoint is derived by prepare_data, so the cleaned CSV need not supply it.
REQUIRED_COLUMNS = tuple(dict.fromkeys(
    column
    for column in ("job_id", "skills", *NUMERIC_COLUMNS, *CATEGORY_COLUMNS)
    if column != MIDPOINT_COLUMN
))
# These tables keep their row labels in the index, so the index is saved too.
INDEXED_TABLES = frozenset({
    "experience_by_remote_counts",
    "experience_by_remote_median_salary",
    "remote_share_by_country",
    "numeric_correlation",
})


def validate_data(df: pd.DataFrame) -> None:
    """Require at least one job and every column used by the analysis."""
    validate_required_columns(df, "Cleaned dataset", REQUIRED_COLUMNS)
    if df.empty:
        raise ValueError("Cleaned dataset has no rows to analyze.")


def ordered_category(series: pd.Series, order: Sequence[str]) -> pd.Categorical:
    """Keep a known label order and still retain unexpected labels."""
    observed = set(series.dropna())
    present = [label for label in order if label in observed]
    extra = sorted(observed - set(order))
    return pd.Categorical(series, categories=present + extra, ordered=True)


def matched_skills_mask(skills: pd.Series) -> pd.Series:
    """Flag rows whose skills text is present and not blank."""
    skills = skills.astype("string")
    return skills.notna() & skills.str.strip().ne("")


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the cleaned data and return a copy with the derived columns.

    The copy gains the salary midpoint, ordered experience and work-arrangement
    labels, and a matched-skills flag. The supplied DataFrame is not changed.
    """
    validate_data(df)
    prepared = df.copy()
    prepared[MIDPOINT_COLUMN] = (
        prepared["salary_min_usd"] + prepared["salary_max_usd"]
    ) / 2
    prepared["experience_level"] = ordered_category(
        prepared["experience_level"], EXPERIENCE_ORDER
    )
    prepared["remote_type"] = ordered_category(prepared["remote_type"], REMOTE_ORDER)
    prepared["skills"] = prepared["skills"].astype("string")
    prepared["has_matched_skills"] = matched_skills_mask(prepared["skills"])
    return prepared


def missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Count missing values per column, with the share of all jobs."""
    missing = df.isna().sum().rename("missing")
    missing_pct = (missing / len(df) * 100).round(2).rename("missing_pct")
    return pd.concat([missing, missing_pct], axis=1).reset_index(names="column")


def numeric_summary(
    df: pd.DataFrame, columns: Sequence[str] = NUMERIC_COLUMNS
) -> pd.DataFrame:
    """Describe numeric columns, adding missing counts and skewness."""
    numeric = df[list(columns)]
    summary = numeric.describe().T
    summary["missing"] = numeric.isna().sum()
    summary["skew"] = numeric.skew(numeric_only=True)
    return summary.reset_index(names="column")


def level_counts(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Count jobs per label of one column, keeping missing labels visible."""
    counts = (
        df[column]
        .value_counts(dropna=False)
        .rename_axis("level")
        .reset_index(name="jobs")
    )
    counts["share_pct"] = (counts["jobs"] / len(df) * 100).round(2)
    return counts


def category_counts(
    df: pd.DataFrame, columns: Sequence[str] = CATEGORY_COLUMNS
) -> pd.DataFrame:
    """Stack the label counts of several columns into one long table."""
    frames = []
    for column in columns:
        counts = level_counts(df, column)
        counts.insert(0, "column", column)
        frames.append(counts)
    return pd.concat(frames, ignore_index=True)


def salary_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Job counts and salary/experience summaries for one categorical column."""
    summary = (
        df.groupby(column, dropna=False, observed=False)
        .agg(
            jobs=("job_id", "size"),
            jobs_with_salary=(MIDPOINT_COLUMN, "count"),
            salary_midpoint_median=(MIDPOINT_COLUMN, "median"),
            salary_midpoint_mean=(MIDPOINT_COLUMN, "mean"),
            experience_years_median=("min_experience_years", "median"),
        )
        .reset_index()
    )
    summary.insert(0, "group", column)
    return summary.rename(columns={column: "level"})


def salary_by_group(
    df: pd.DataFrame, columns: Sequence[str] = GROUP_COLUMNS
) -> pd.DataFrame:
    """Stack the salary summaries of several grouping columns into one table."""
    return pd.concat(
        [salary_summary(df, column) for column in columns], ignore_index=True
    )


def cross_counts(df: pd.DataFrame, rows: str, columns: str) -> pd.DataFrame:
    """Count jobs for each pair of labels, with row and column totals."""
    return pd.crosstab(df[rows], df[columns], dropna=False, margins=True)


def cross_median(
    df: pd.DataFrame, rows: str, columns: str, values: str = MIDPOINT_COLUMN
) -> pd.DataFrame:
    """Median of a numeric column for each pair of labels."""
    return pd.pivot_table(
        df,
        index=rows,
        columns=columns,
        values=values,
        aggfunc="median",
        observed=False,
    )


def row_share(df: pd.DataFrame, rows: str, columns: str) -> pd.DataFrame:
    """Percentage split of each row label across the column labels, plus job counts."""
    share = (
        pd.crosstab(df[rows], df[columns], normalize="index", dropna=False)
        .mul(100)
        .round(2)
    )
    share["jobs"] = df.groupby(rows, dropna=False).size()
    return share


def numeric_correlation(
    df: pd.DataFrame, columns: Sequence[str] = NUMERIC_COLUMNS
) -> pd.DataFrame:
    """Pairwise correlation matrix for the numeric columns."""
    return df[list(columns)].corr(numeric_only=True).round(3)


def pair_correlation(df: pd.DataFrame, first: str, second: str) -> tuple[int, float]:
    """Correlate two columns using only jobs that have both values.

    Returns the number of jobs used and the coefficient.
    """
    pair = df[[first, second]].dropna()
    return len(pair), pair[first].corr(pair[second])


def skill_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Count the jobs that list each skill, among jobs with matched skills.

    A job is counted once per skill. Jobs without a skill match are left out,
    which does not mean that they require no skills.
    """
    skills = df["skills"].astype("string")
    matched = matched_skills_mask(skills)
    jobs_with_skills = int(matched.sum())
    skill_rows = (
        df.loc[matched, ["job_id"]]
        .assign(skill=skills[matched].str.split(r"\s*;\s*"))
        .explode("skill")
    )
    skill_rows["skill"] = skill_rows["skill"].str.strip()
    skill_rows = skill_rows.loc[skill_rows["skill"].ne("") & skill_rows["skill"].notna()]
    counts = (
        skill_rows.groupby("skill")["job_id"]
        .nunique()
        .sort_values(ascending=False)
        .rename("jobs")
        .reset_index()
    )
    if jobs_with_skills:
        counts["share_of_matched_jobs_pct"] = (
            counts["jobs"] / jobs_with_skills * 100
        ).round(2)
    else:
        counts["share_of_matched_jobs_pct"] = pd.Series(dtype="float64")
    return counts


def build_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Calculate every summary table from data returned by prepare_data.

    Each key is also the name of the CSV file the table is saved to.
    """
    return {
        "missing_values": missing_values(df),
        "numeric_summary": numeric_summary(df),
        "category_counts": category_counts(df),
        "salary_by_group": salary_by_group(df),
        "experience_by_remote_counts": cross_counts(
            df, "experience_level", "remote_type"
        ),
        "experience_by_remote_median_salary": cross_median(
            df, "experience_level", "remote_type"
        ),
        "remote_share_by_country": row_share(df, "country", "remote_type"),
        "numeric_correlation": numeric_correlation(df),
        "skill_counts": skill_counts(df),
    }
