from pathlib import Path

import pandas as pd


CLEANING_DIR = Path(__file__).resolve().parent
INPUT_PATH = CLEANING_DIR.parent / "02_Database" / "consolidated_data_database.csv"
OUTPUT_PATH = CLEANING_DIR / "clean_data.csv"


if __name__ == "__main__":
    # Step 1: Read Data.
    # Read as strings first to preserve IDs and detect numeric conversion failures.
    df = pd.read_csv(INPUT_PATH, dtype="string")

    # Step 2: Inspect Data.
    original_rows = len(df)
    original_missing = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())
    print(f"Initial dimensions: {original_rows:,} rows, {len(df.columns)} columns")
    print("\nInitial data types (loaded as strings):")
    print(df.dtypes.to_string())
    print("\nInitial missing values:")
    print(original_missing.to_string())
    print(f"\nExact duplicate rows: {duplicate_rows:,}")
    print(f"Missing job IDs: {df['job_id'].fillna('').str.strip().eq('').sum():,}")
    print(f"Repeated job IDs beyond the first occurrence: {df['job_id'].duplicated().sum():,}")

    # Step 3: Clean and Prepare Data.
    # Remove only identical records; never arbitrarily select among conflicting jobs.
    df = df.drop_duplicates().copy()
    missing_ids = df["job_id"].fillna("").str.strip().eq("")
    conflicting_ids = df["job_id"].notna() & df["job_id"].duplicated(keep=False)
    if missing_ids.any() or conflicting_ids.any():
        print(f"Missing job IDs after deduplication: {missing_ids.sum():,}")
        print(f"Rows with conflicting duplicate IDs: {conflicting_ids.sum():,}")
        print("Conflicting ID examples:", df.loc[conflicting_ids, "job_id"].unique()[:10])
        raise ValueError("Resolve missing or conflicting job IDs before saving clean data.")

    # Whitespace-only fields are missing. Preserve job IDs exactly as supplied.
    for column in df.columns:
        if column != "job_id":
            df[column] = df[column].mask(df[column].str.strip().eq(""), pd.NA)

    # Normalize known labels without guessing synonyms or rewriting unknown labels.
    # These canonical names come from the project's source datasets.
    category_labels = {
        "job_title": [
            "Data Scientist", "Machine Learning Engineer", "AI Researcher",
            "Data Analyst", "Applied Scientist", "MLOps Engineer",
        ],
        "country": ["USA", "India", "UK", "Germany", "Canada", "Australia"],
        "experience_level": ["Entry", "Mid", "Senior"],
        "remote_type": ["Remote", "Hybrid", "Onsite"],
    }
    for column, labels in category_labels.items():
        before = df[column].copy()
        trimmed = before.str.strip()
        label_map = {label.casefold(): label for label in labels}
        normalized = trimmed.str.casefold().map(label_map)
        df[column] = normalized.fillna(trimmed).astype("string")
        changed = before.notna() & before.ne(df[column]).fillna(False)
        print(f"{column}: standardized {changed.sum():,} labels")
        unknown = df.loc[df[column].notna() & ~df[column].isin(labels), column].unique()
        if len(unknown):
            print(f"  Unrecognized labels retained for review: {list(unknown)}")

    # Use nullable numeric types so missing values remain missing, not zero.
    numeric_columns = [
        "salary_min_usd", "salary_max_usd", "min_experience_years", "posted_year",
        "country_total_ai_jobs", "country_avg_salary_usd", "country_remote_percentage",
    ]
    for column in numeric_columns:
        before = df[column]
        converted = pd.to_numeric(before, errors="coerce").astype("Float64")
        conversion_failures = before.notna() & converted.isna()
        non_finite = converted.isin([float("inf"), float("-inf")])
        print(
            f"{column}: {conversion_failures.sum():,} unconvertible values, "
            f"{non_finite.sum():,} infinite values set to missing"
        )
        df[column] = converted.mask(non_finite, pd.NA)

    # Identify reversed ranges before removing negatives so both rules apply.
    reversed_salary = (df["salary_min_usd"] > df["salary_max_usd"]).fillna(False)
    for column in ["salary_min_usd", "salary_max_usd"]:
        negative = (df[column] < 0).fillna(False)
        print(f"{column}: {negative.sum():,} negative values set to missing")
        df.loc[negative, column] = pd.NA
    df.loc[reversed_salary, ["salary_min_usd", "salary_max_usd"]] = pd.NA
    print(f"Reversed salary ranges: {reversed_salary.sum():,}; both bounds set to missing")

    # Zero years of experience is valid; negative values are not.
    negative_experience = (df["min_experience_years"] < 0).fillna(False)
    df.loc[negative_experience, "min_experience_years"] = pd.NA
    print(f"Negative experience values set to missing: {negative_experience.sum():,}")

    # Retain all valid posting years; selecting the current period belongs to EDA.
    valid_year = (
        df["posted_year"].between(2020, 2026)
        & df["posted_year"].mod(1).eq(0)
    ).fillna(False)
    invalid_year = df["posted_year"].notna() & ~valid_year
    df.loc[invalid_year, "posted_year"] = pd.NA
    df["posted_year"] = df["posted_year"].astype("Int64")
    print(f"Invalid posting years set to missing: {invalid_year.sum():,}")

    # Keep jobs even when skills, country statistics, salaries, or experience
    # are missing. Missing skills do not mean that no skills are required.
    print(f"\nRows before cleaning: {original_rows:,}")
    print(f"Exact duplicates removed: {duplicate_rows:,}")
    print(f"Rows after cleaning: {len(df):,}")
    print("\nMissing values before and after cleaning:")
    print(pd.DataFrame({"before": original_missing, "after": df.isna().sum()}).to_string())
    print("\nFinal data types:")
    print(df.dtypes.to_string())

    # Step 4: Save Clean Data.
    # Export only after validation succeeds; leave the source CSV and database intact.
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nClean data saved to: {OUTPUT_PATH}")
