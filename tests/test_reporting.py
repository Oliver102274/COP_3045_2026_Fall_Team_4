"""Reporting regression tests: python -B -m unittest discover -s tests -v."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("MPLBACKEND", "Agg")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "05-Report"
sys.path.insert(0, str(REPORT_DIR))

import pandas as pd
from pandas.testing import assert_frame_equal

from reporting import ReportGenerator
from reporting.analysis import (
    calculate_findings, calculate_summary, load_data, validate_data,
)
from reporting.charts import plot_standardized_titles


def sample_data() -> pd.DataFrame:
    """Return small data with ties, missing salaries, and blank work arrangements."""
    return pd.DataFrame({
        "standardized_title": ["Analyst", "Engineer", "Analyst", "Engineer"],
        "country": ["USA", "UK", "USA", "UK"],
        "experience_level": ["Entry", "Senior", "Entry", "Senior"],
        "remote_type": ["Hybrid", "Remote", " ", None],
        "skills": ["Python", None, " ", "SQL"],
        "min_experience_years": [0, 4, 2, 6],
        "salary_min_usd": [10.0, 30.0, None, 50.0],
        "salary_max_usd": [20.0, 40.0, 60.0, None],
        "posted_year": [2020, 2021, 2020, 2021],
    })


class AnalysisTests(unittest.TestCase):
    """Verify statistical meaning and validation without mutating source data."""

    def test_dynamic_statistics_ties_and_denominators(self) -> None:
        df = sample_data()
        before = df.copy(deep=True)
        validate_data(df)
        summary = calculate_summary(df)
        findings = calculate_findings(df)
        self.assertEqual(summary["row_count"], 4)
        self.assertEqual(summary["column_count"], 9)
        self.assertEqual(summary["first_year"], 2020)
        self.assertEqual(summary["last_year"], 2021)
        self.assertEqual(summary["summary_statistics"].loc["salary_min_usd", "mean"], 30)
        self.assertEqual(summary["summary_statistics"].loc["min_experience_years", "median"], 3)
        self.assertEqual(set(findings["most_frequent_titles_text"].split(", ")), {"Analyst", "Engineer"})
        self.assertEqual(findings["most_frequent_title_count"], 2)
        self.assertEqual(findings["highest_mean_salary"], 40)
        self.assertEqual(findings["highest_salary_levels_text"], "Entry, Senior")
        self.assertEqual(set(findings["most_common_remote_types_text"].split(", ")), {"Hybrid", "Remote"})
        self.assertEqual(findings["remote_percentage"], 50)
        self.assertEqual(findings["highest_posting_years_text"], "2020, 2021")
        self.assertEqual(findings["skills_percentage"], 50)
        assert_frame_equal(df, before)

    def test_project_baseline(self) -> None:
        df = load_data(PROJECT_ROOT / "03_Data_Cleaning" / "clean_data.csv")
        summary = calculate_summary(df)
        findings = calculate_findings(df)
        self.assertEqual((summary["row_count"], summary["column_count"]), (50000, 21))
        self.assertEqual((summary["first_year"], summary["last_year"]), (2020, 2026))
        self.assertEqual((summary["country_count"], summary["title_count"]), (6, 6))
        self.assertEqual(findings["most_frequent_titles_text"], "MLOps Engineer")
        self.assertEqual(findings["most_frequent_title_count"], 8439)
        self.assertEqual(findings["highest_salary_levels_text"], "Senior")
        self.assertAlmostEqual(findings["highest_mean_salary"], 167496.16903519817)
        self.assertEqual(findings["most_common_remote_types_text"], "Hybrid")
        self.assertEqual(findings["most_common_remote_count"], 16984)
        self.assertEqual(findings["highest_posting_years_text"], "2024")
        self.assertEqual(findings["year_highest_count"], 7312)
        self.assertEqual(findings["skills_count"], 2050)
        self.assertAlmostEqual(findings["skills_percentage"], 4.1)

    def test_empty_dataset(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_data(sample_data().iloc[:0])

    def test_missing_columns(self) -> None:
        with self.assertRaisesRegex(ValueError, "required columns: country, skills"):
            validate_data(sample_data().drop(columns=["country", "skills"]))

    def test_invalid_numeric_fields(self) -> None:
        for value in ["invalid", True, float("inf"), complex(1, 2)]:
            with self.subTest(value=value):
                df = sample_data()
                df["salary_max_usd"] = value
                with self.assertRaisesRegex(ValueError, "salary_max_usd"):
                    validate_data(df)

    def test_all_missing_numeric_values(self) -> None:
        df = sample_data()
        df["posted_year"] = float("nan")
        with self.assertRaisesRegex(ValueError, "posted_year.*no numeric values"):
            validate_data(df)

    def test_unusable_categories(self) -> None:
        for column, value, message in [
            ("remote_type", " ", "nonblank work arrangements"),
            ("standardized_title", None, "No standardized titles"),
            ("experience_level", None, "No experience levels"),
        ]:
            with self.subTest(column=column):
                df = sample_data()
                df[column] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_data(df)

    def test_missing_skills_are_allowed(self) -> None:
        df = sample_data()
        df["skills"] = None
        validate_data(df)
        self.assertEqual(calculate_findings(df)["skills_count"], 0)

    def test_missing_and_empty_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            with self.assertRaisesRegex(FileNotFoundError, "Reporting input CSV not found"):
                load_data(path)
            path.write_text("")
            with self.assertRaisesRegex(ValueError, "CSV is empty"):
                load_data(path)
            sample_data().iloc[:0].to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "dataset is empty"):
                load_data(path)

    def test_invalid_csv_contents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text('column\n"unterminated')
            with self.assertRaisesRegex(ValueError, "Could not read reporting input CSV"):
                load_data(path)


class ReportingTests(unittest.TestCase):
    """Check reporting boundaries and failures using temporary output directories."""

    def test_imports_and_constructor_have_no_generation_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            code = (
                "from pathlib import Path; import reporting; "
                "import reporting.analysis, reporting.charts, reporting.report; "
                "import generate_report; "
                "reporting.ReportGenerator(Path('missing.csv'), Path('output'))"
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPORT_DIR)
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=directory,
                env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_invalid_input_does_not_create_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                ReportGenerator(root / "missing.csv", root / "output").generate()
            self.assertFalse((root / "output").exists())

    def test_output_directory_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_file = root / "input.csv"
            sample_data().to_csv(data_file, index=False)
            blocked = root / "blocked"
            blocked.write_text("Existing file must remain unchanged.")
            with self.assertRaisesRegex(RuntimeError, "prepare report output directory"):
                ReportGenerator(data_file, blocked).generate()
            self.assertEqual(blocked.read_text(), "Existing file must remain unchanged.")

    def test_chart_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("reporting.charts.plt.savefig", side_effect=PermissionError("denied")):
                with self.assertRaisesRegex(RuntimeError, "standardized_title_postings.png.*denied"):
                    plot_standardized_titles(sample_data(), Path(directory))

    def test_pdf_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_file = root / "input.csv"
            sample_data().to_csv(data_file, index=False)
            # Exercise real PDF construction; fail only the final filesystem write.
            with patch("reporting.report.FPDF.output", side_effect=PermissionError("denied")):
                with self.assertRaisesRegex(RuntimeError, "Could not generate PDF.*denied"):
                    ReportGenerator(data_file, root / "output").generate()

    def test_chart_failure_prevents_pdf_generation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_file = root / "input.csv"
            sample_data().to_csv(data_file, index=False)
            with patch("reporting.report.generate_charts", side_effect=RuntimeError("chart failed")):
                with patch.object(ReportGenerator, "_write_pdf") as write_pdf:
                    with self.assertRaisesRegex(RuntimeError, "chart failed"):
                        ReportGenerator(data_file, root / "output").generate()
                    write_pdf.assert_not_called()

    def test_launcher_failure_exit_code(self) -> None:
        import generate_report

        with patch.object(generate_report.ReportGenerator, "generate", side_effect=ValueError("bad data")):
            with patch("sys.stderr") as error_stream:
                with self.assertRaises(SystemExit) as error:
                    generate_report.main()
                self.assertEqual(error.exception.code, 1)
                self.assertIn("Reporting failed: bad data", str(error_stream.write.call_args_list))


if __name__ == "__main__":
    unittest.main()
