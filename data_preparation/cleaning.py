"""Object-oriented cleaning with the original data preparation rules."""

from pathlib import Path

import pandas as pd

from .validation import validate_required_columns


class DataCleaner:
    """Clean analytical data; underscore names mark internal details by convention."""

    def __init__(self, input_path: Path, output_path: Path) -> None:
        """Store paths without accessing files or creating output directories."""
        self._input_path = Path(input_path)
        self._output_path = Path(output_path)

    def run(self) -> pd.DataFrame:
        """Load string-valued data, clean it, save it, and return the result."""
        if self._input_path.resolve() == self._output_path.resolve():
            raise ValueError("Cleaning input and output paths must be different.")
        try:
            df = pd.read_csv(self._input_path, dtype="string")
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError) as error:
            raise ValueError(f"Cannot parse cleaning input {self._input_path}: {error}") from error
        except OSError as error:
            raise OSError(f"Cannot read cleaning input {self._input_path}: {error}") from error
        cleaned = self.clean_dataframe(df)
        try:
            cleaned.to_csv(self._output_path, index=False)
        except OSError as error:
            raise OSError(f"Cannot save clean data to {self._output_path}: {error}") from error
        print(f"\nClean data saved to: {self._output_path}")
        return cleaned

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean a copy and print diagnostics without file access.

        Supply string-valued columns as produced by read_csv(dtype="string"),
        with missing values represented by pandas missing values. Other dtypes
        are rejected to avoid silently changing parsing or identifier semantics.
        """
        required = [
            "job_id", "job_title", "country", "experience_level", "remote_type",
            "salary_min_usd", "salary_max_usd", "min_experience_years", "posted_year",
            "country_total_ai_jobs", "country_avg_salary_usd", "country_remote_percentage",
        ]
        validate_required_columns(df, "cleaning input", required)
        for column in df.columns:
            if not isinstance(df[column].dtype, pd.StringDtype):
                raise ValueError(f"Cleaning input column {column} must use pandas string dtype.")
        df = df.copy(deep=True)
        original_rows, original_missing, duplicate_rows = self._inspect(df)
        df = self._deduplicate_and_validate_ids(df)
        self._normalize_text(df)
        self._convert_numeric(df)
        self._mask_invalid_values(df)
        self._print_summary(df, original_rows, original_missing, duplicate_rows)
        return df

    def _inspect(self, df: pd.DataFrame) -> tuple[int, pd.Series, int]:
        """Print original dimensions, types, missing values, and duplicate counts."""
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

        return original_rows, original_missing, duplicate_rows

    def _deduplicate_and_validate_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicate rows and reject missing or conflicting IDs."""
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

        return df

    def _normalize_text(self, df: pd.DataFrame) -> None:
        """Mask blank non-ID fields and normalize the existing known labels."""
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

    def _convert_numeric(self, df: pd.DataFrame) -> None:
        """Convert the seven numeric columns and mask infinite values."""
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

    def _mask_invalid_values(self, df: pd.DataFrame) -> None:
        """Apply salary, experience, and fixed posting-year rules in order."""
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

    def _print_summary(self, df: pd.DataFrame, original_rows: int, original_missing: pd.Series, duplicate_rows: int) -> None:
        """Report before/after row counts, missing values, and final types."""
        # Keep jobs even when skills, country statistics, salaries, or experience
        # are missing. Missing skills do not mean that no skills are required.
        print(f"\nRows before cleaning: {original_rows:,}")
        print(f"Exact duplicates removed: {duplicate_rows:,}")
        print(f"Rows after cleaning: {len(df):,}")
        print("\nMissing values before and after cleaning:")
        print(pd.DataFrame({"before": original_missing, "after": df.isna().sum()}).to_string())
        print("\nFinal data types:")
        print(df.dtypes.to_string())

