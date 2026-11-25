"""Coordinate loading, table calculation, console reporting, and saving."""

from pathlib import Path

import pandas as pd

from .tables import (
    CATEGORY_COLUMNS, INDEXED_TABLES, MIDPOINT_COLUMN, build_tables, level_counts,
    pair_correlation, prepare_data,
)


class NonGraphicalAnalyzer:
    """Describe the cleaned dataset; underscore names mark internal details by convention."""

    def __init__(self, input_path: Path, output_dir: Path) -> None:
        """Store paths without reading data or creating the output directory."""
        self._input_path = Path(input_path)
        self._output_dir = Path(output_dir)

    def run(self) -> dict[str, pd.DataFrame]:
        """Load the cleaned data, print the analysis, save the tables, and return them."""
        df = self.load_data()
        prepared = prepare_data(df)
        tables = build_tables(prepared)
        self._print_section("1. Read data")
        print(f"Source: {self._input_path}")
        print(f"Jobs: {len(df):,} | Columns: {len(df.columns)}")
        self._print_report(prepared, tables)
        self.save_tables(tables)
        self._print_section("10. Saved tables")
        print(f"Summary tables written to: {self._output_dir}")
        return tables

    def load_data(self) -> pd.DataFrame:
        """Read the cleaned CSV, giving file and parsing failures clear context."""
        if not self._input_path.is_file():
            raise FileNotFoundError(f"Cleaned dataset not found: {self._input_path}")
        try:
            return pd.read_csv(self._input_path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeError) as error:
            raise ValueError(
                f"Cannot parse cleaned dataset {self._input_path}: {error}"
            ) from error
        except OSError as error:
            raise OSError(
                f"Cannot read cleaned dataset {self._input_path}: {error}"
            ) from error

    def save_tables(self, tables: dict[str, pd.DataFrame]) -> None:
        """Write each table to '<name>.csv' in the output directory."""
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            for name, table in tables.items():
                table.to_csv(
                    self._output_dir / f"{name}.csv", index=name in INDEXED_TABLES
                )
        except OSError as error:
            raise OSError(
                f"Cannot save analysis tables to {self._output_dir}: {error}"
            ) from error

    def _print_report(self, df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
        """Print sections 2-9 from the prepared data and its calculated tables."""
        self._print_section("2. Missing values")
        print(tables["missing_values"].to_string(index=False))

        self._print_section("3. Numeric summaries")
        print(tables["numeric_summary"].round(2).to_string(index=False))
        print(
            "Salary midpoint uses only jobs with both bounds. "
            f"Jobs with a midpoint: {df[MIDPOINT_COLUMN].notna().sum():,} of {len(df):,}."
        )

        self._print_section("4. Category counts")
        # Counted per column so each label keeps its own type when printed;
        # the stacked table mixes text and year labels in one column.
        for column in CATEGORY_COLUMNS:
            print(f"\n{column}")
            print(level_counts(df, column).to_string(index=False))

        self._print_section("5. Salary and experience by group")
        grouped_salary = tables["salary_by_group"]
        for column in grouped_salary["group"].unique():
            print(f"\n{column}")
            view = grouped_salary.loc[grouped_salary["group"] == column]
            print(view.drop(columns="group").round(2).to_string(index=False))

        self._print_section("6. Experience level by remote type")
        print("Job counts")
        print(tables["experience_by_remote_counts"].to_string())
        print("\nMedian salary midpoint (USD)")
        print(tables["experience_by_remote_median_salary"].round(2).to_string())

        self._print_section("7. Remote share by country")
        print(tables["remote_share_by_country"].to_string())

        self._print_section("8. Numeric correlations")
        print(tables["numeric_correlation"].to_string())
        jobs, coefficient = pair_correlation(df, "min_experience_years", MIDPOINT_COLUMN)
        print(
            "\nJobs used for experience-to-salary correlation: "
            f"{jobs:,}. Coefficient: {coefficient:.3f}."
        )
        jobs, coefficient = pair_correlation(df, MIDPOINT_COLUMN, "country_avg_salary_usd")
        print(
            "Jobs used for job-midpoint to country-average correlation: "
            f"{jobs:,}. Coefficient: {coefficient:.3f}."
        )
        print(
            "country_avg_salary_usd and country_remote_percentage describe the "
            "country-year, not the individual job."
        )

        self._print_section("9. Matched skills")
        print(f"Jobs with matched skills: {int(df['has_matched_skills'].sum()):,} of {len(df):,}.")
        print(
            "Most jobs have no skill match. Frequencies below describe matched jobs only "
            "and do not mean unmatched jobs require no skills."
        )
        print(tables["skill_counts"].to_string(index=False))

    @staticmethod
    def _print_section(title: str) -> None:
        """Print a numbered-looking heading so console output stays scannable."""
        print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")
