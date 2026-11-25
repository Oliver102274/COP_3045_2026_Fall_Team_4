"""Non-graphical EDA tests use small synthetic data and temporary outputs."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EDA_DIR = PROJECT_ROOT / "04_EDA"
for import_root in (PROJECT_ROOT, EDA_DIR):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import nongraphical_analysis  # noqa: E402
from nongraphical import NonGraphicalAnalyzer, build_tables, prepare_data  # noqa: E402
from nongraphical import tables as eda_tables  # noqa: E402

TABLE_NAMES = [
    "missing_values", "numeric_summary", "category_counts", "salary_by_group",
    "experience_by_remote_counts", "experience_by_remote_median_salary",
    "remote_share_by_country", "numeric_correlation", "skill_counts",
]


def sample_data() -> pd.DataFrame:
    """Return six jobs with a missing salary bound, an unexpected level, and blank skills."""
    return pd.DataFrame({
        "job_id": ["J1", "J2", "J3", "J4", "J5", "J6"],
        "experience_level": ["Entry", "Mid", "Senior", "Senior", "Lead", "Entry"],
        "remote_type": ["Remote", "Hybrid", "Onsite", "Remote", "Hybrid", "Remote"],
        "country": ["USA", "USA", "UK", "UK", "India", "India"],
        "company_type": ["Startup", "MNC", "Startup", "MNC", "Startup", "MNC"],
        "company_size": ["Small", "Large", "Small", "Large", "Small", "Large"],
        "industry": ["Tech", "Tech", "Finance", "Finance", "Retail", "Retail"],
        "employment_type": ["Full-time"] * 6,
        "role_category": ["Analytics", "Engineering"] * 3,
        "posted_year": [2024, 2024, 2025, 2025, 2026, 2026],
        "salary_min_usd": [100.0, 200.0, 300.0, 400.0, None, 100.0],
        "salary_max_usd": [200.0, 400.0, 500.0, 600.0, 900.0, 300.0],
        "min_experience_years": [0, 2, 5, 6, 8, 1],
        "country_total_ai_jobs": [10, 10, 20, 20, 30, 30],
        "country_avg_salary_usd": [150.0, 150.0, 450.0, 450.0, 200.0, 200.0],
        "country_remote_percentage": [50.0, 50.0, 40.0, 40.0, 60.0, 60.0],
        "skills": ["Python; SQL", " Python ;Python", None, "  ", "SQL", None],
    })


class TableTests(unittest.TestCase):
    """Verify each table calculation without printing or file access."""

    def setUp(self) -> None:
        self.prepared = prepare_data(sample_data())

    def test_prepare_data_adds_columns_without_changing_input(self) -> None:
        df = sample_data()
        before = df.copy(deep=True)
        prepared = prepare_data(df)
        assert_frame_equal(df, before)
        midpoint = prepared["salary_midpoint_usd"]
        self.assertEqual(midpoint.dropna().tolist(), [150, 300, 400, 500, 200])
        self.assertTrue(pd.isna(midpoint[4]))
        # Known labels keep their order; unexpected labels are retained after them.
        self.assertEqual(
            list(prepared["experience_level"].cat.categories),
            ["Entry", "Mid", "Senior", "Lead"],
        )
        self.assertEqual(
            list(prepared["remote_type"].cat.categories), ["Remote", "Hybrid", "Onsite"]
        )
        self.assertEqual(
            prepared["has_matched_skills"].tolist(),
            [True, True, False, False, True, False],
        )

    def test_missing_columns_and_empty_data_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, r"missing required columns: \['skills', 'country'\]"):
            prepare_data(sample_data().drop(columns=["country", "skills"]))
        with self.assertRaisesRegex(ValueError, "no rows"):
            prepare_data(sample_data().iloc[:0])

    def test_missing_values(self) -> None:
        table = eda_tables.missing_values(self.prepared).set_index("column")
        self.assertEqual(table.loc["salary_min_usd", "missing"], 1)
        self.assertEqual(table.loc["salary_min_usd", "missing_pct"], 16.67)
        # A whitespace-only skills value is blank text, not a missing value.
        self.assertEqual(table.loc["skills", "missing"], 2)
        self.assertEqual(table.loc["job_id", "missing"], 0)

    def test_numeric_summary(self) -> None:
        table = eda_tables.numeric_summary(self.prepared).set_index("column")
        self.assertEqual(list(table.index), list(eda_tables.NUMERIC_COLUMNS))
        self.assertEqual(table.loc["salary_midpoint_usd", "count"], 5)
        self.assertEqual(table.loc["salary_midpoint_usd", "missing"], 1)
        self.assertEqual(table.loc["salary_midpoint_usd", "50%"], 300)
        self.assertEqual(table.loc["min_experience_years", "max"], 8)
        summary = eda_tables.numeric_summary(self.prepared, ["posted_year"])
        self.assertEqual(summary["column"].tolist(), ["posted_year"])

    def test_category_counts(self) -> None:
        table = eda_tables.category_counts(self.prepared)
        self.assertEqual(list(table.columns), ["column", "level", "jobs", "share_pct"])
        self.assertEqual(
            list(table["column"].unique()), list(eda_tables.CATEGORY_COLUMNS)
        )
        levels = table[table["column"] == "experience_level"].set_index("level")
        self.assertEqual(
            levels["jobs"].to_dict(), {"Entry": 2, "Senior": 2, "Mid": 1, "Lead": 1}
        )
        self.assertEqual(levels.loc["Entry", "share_pct"], 33.33)
        self.assertTrue((table.groupby("column")["jobs"].sum() == 6).all())

    def test_level_counts_keep_missing_labels(self) -> None:
        df = sample_data()
        df.loc[0, "country"] = None
        counts = eda_tables.level_counts(df, "country")
        self.assertEqual(counts["jobs"].sum(), 6)
        self.assertEqual(counts.loc[counts["level"].isna(), "jobs"].tolist(), [1])

    def test_salary_by_group(self) -> None:
        table = eda_tables.salary_by_group(self.prepared)
        self.assertEqual(list(table["group"].unique()), list(eda_tables.GROUP_COLUMNS))
        self.assertNotIn("employment_type", table["group"].tolist())
        india = table[(table["group"] == "country") & (table["level"] == "India")].iloc[0]
        # Both jobs are counted, but only one has a salary midpoint.
        self.assertEqual((india["jobs"], india["jobs_with_salary"]), (2, 1))
        self.assertEqual(india["salary_midpoint_median"], 200)
        levels = table.loc[table["group"] == "experience_level", "level"].tolist()
        self.assertEqual(levels, ["Entry", "Mid", "Senior", "Lead"])
        single = eda_tables.salary_summary(self.prepared, "industry").set_index("level")
        self.assertEqual(single.loc["Tech", "salary_midpoint_mean"], 225)
        self.assertEqual(single.loc["Finance", "experience_years_median"], 5.5)

    def test_cross_tables(self) -> None:
        counts = eda_tables.cross_counts(self.prepared, "experience_level", "remote_type")
        self.assertEqual(counts.loc["All", "All"], 6)
        self.assertEqual(counts.loc["Senior", "Remote"], 1)
        self.assertEqual(counts.loc["Entry", "All"], 2)
        median = eda_tables.cross_median(self.prepared, "experience_level", "remote_type")
        self.assertEqual(median.loc["Entry", "Remote"], 175)
        self.assertTrue(pd.isna(median.loc["Mid", "Remote"]))
        share = eda_tables.row_share(self.prepared, "country", "remote_type")
        self.assertEqual(
            share.loc["USA"].to_dict(),
            {"Remote": 50.0, "Hybrid": 50.0, "Onsite": 0.0, "jobs": 2.0},
        )
        self.assertEqual(share["jobs"].sum(), 6)

    def test_correlations_use_complete_pairs(self) -> None:
        jobs, coefficient = eda_tables.pair_correlation(
            self.prepared, "min_experience_years", "salary_midpoint_usd"
        )
        expected = np.corrcoef([0, 2, 5, 6, 1], [150, 300, 400, 500, 200])[0, 1]
        self.assertEqual(jobs, 5)
        self.assertAlmostEqual(coefficient, expected)
        matrix = eda_tables.numeric_correlation(self.prepared)
        self.assertEqual(matrix.shape, (8, 8))
        self.assertEqual(list(matrix.index), list(eda_tables.NUMERIC_COLUMNS))
        self.assertTrue((np.diag(matrix) == 1).all())
        self.assertEqual(
            matrix.loc["min_experience_years", "salary_midpoint_usd"], round(expected, 3)
        )

    def test_skill_counts(self) -> None:
        table = eda_tables.skill_counts(self.prepared)
        # A skill repeated within one job counts once; blank skills match nothing.
        self.assertEqual(dict(zip(table["skill"], table["jobs"])), {"Python": 2, "SQL": 2})
        self.assertEqual(table["share_of_matched_jobs_pct"].tolist(), [66.67, 66.67])
        # The raw cleaned frame gives the same counts as the prepared one.
        assert_frame_equal(eda_tables.skill_counts(sample_data()), table)

    def test_skill_counts_without_matches(self) -> None:
        df = sample_data()
        df["skills"] = None
        table = eda_tables.skill_counts(df)
        self.assertEqual(
            list(table.columns), ["skill", "jobs", "share_of_matched_jobs_pct"]
        )
        self.assertTrue(table.empty)
        self.assertEqual(int(prepare_data(df)["has_matched_skills"].sum()), 0)

    def test_build_tables_names_and_indexed_tables(self) -> None:
        tables = build_tables(self.prepared)
        self.assertEqual(list(tables), TABLE_NAMES)
        self.assertLess(eda_tables.INDEXED_TABLES, set(TABLE_NAMES))

    def test_project_baseline(self) -> None:
        df = pd.read_csv(PROJECT_ROOT / "03_Data_Cleaning" / "clean_data.csv")
        prepared = prepare_data(df)
        tables = build_tables(prepared)
        self.assertEqual(len(prepared), 50000)
        missing = tables["missing_values"].set_index("column")["missing"]
        self.assertEqual(missing["skills"], 47950)
        self.assertEqual(int(prepared["has_matched_skills"].sum()), 2050)
        top_skill = tables["skill_counts"].iloc[0]
        self.assertEqual((top_skill["skill"], top_skill["jobs"]), ("TensorFlow", 876))
        salary = tables["salary_by_group"]
        senior = salary[(salary["group"] == "experience_level") & (salary["level"] == "Senior")]
        self.assertEqual(senior["salary_midpoint_median"].item(), 157468.5)
        self.assertEqual(tables["experience_by_remote_counts"].loc["All", "All"], 50000)
        self.assertEqual(tables["remote_share_by_country"].loc["UK", "jobs"], 8452)
        self.assertEqual(
            tables["numeric_correlation"].loc["min_experience_years", "salary_midpoint_usd"],
            0.992,
        )


class AnalyzerTests(unittest.TestCase):
    """Check the file workflow and its failures using temporary directories."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.input = self.root / "clean_data.csv"
        self.output = self.root / "output"
        self.analyzer = NonGraphicalAnalyzer(self.input, self.output)

    def run_analyzer(self) -> tuple[dict[str, pd.DataFrame], str]:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            tables = self.analyzer.run()
        return tables, output.getvalue()

    def test_run_prints_saves_and_returns_tables(self) -> None:
        sample_data().to_csv(self.input, index=False)
        tables, printed = self.run_analyzer()
        self.assertEqual(list(tables), TABLE_NAMES)
        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            sorted(f"{name}.csv" for name in TABLE_NAMES),
        )
        for number, title in enumerate([
            "Read data", "Missing values", "Numeric summaries", "Category counts",
            "Salary and experience by group", "Experience level by remote type",
            "Remote share by country", "Numeric correlations", "Matched skills",
            "Saved tables",
        ], start=1):
            self.assertIn(f"\n{number}. {title}\n", printed)
        self.assertIn("Jobs: 6 | Columns: 17", printed)
        self.assertIn("Jobs with a midpoint: 5 of 6.", printed)
        self.assertIn("Jobs with matched skills: 3 of 6.", printed)
        saved = pd.read_csv(self.output / "skill_counts.csv")
        assert_frame_equal(saved, tables["skill_counts"], check_dtype=False)
        # Tables with labels in the index keep them as the first saved column.
        counts = pd.read_csv(self.output / "experience_by_remote_counts.csv", index_col=0)
        self.assertEqual(counts.loc["All", "All"], 6)

    def test_repeated_runs_give_the_same_tables(self) -> None:
        sample_data().to_csv(self.input, index=False)
        first, _ = self.run_analyzer()
        second, _ = self.run_analyzer()
        for name in TABLE_NAMES:
            assert_frame_equal(first[name], second[name])

    def test_imports_and_constructor_have_no_side_effects(self) -> None:
        code = (
            "from pathlib import Path; import nongraphical, nongraphical_analysis; "
            "import nongraphical.tables, nongraphical.analyzer; "
            "nongraphical.NonGraphicalAnalyzer(Path('missing.csv'), Path('output'))"
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([str(EDA_DIR), str(PROJECT_ROOT)])
        result = subprocess.run(
            [sys.executable, "-B", "-c", code], cwd=self.root,
            env=env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(list(self.root.iterdir()), [])

    def test_missing_input_does_not_create_outputs(self) -> None:
        with self.assertRaisesRegex(FileNotFoundError, "Cleaned dataset not found"):
            self.run_analyzer()
        self.assertFalse(self.output.exists())

    def test_unusable_input_does_not_create_outputs(self) -> None:
        header = ",".join(sample_data().columns)
        for contents, message in [
            ("", "Cannot parse cleaned dataset"),
            ('column\n"unterminated', "Cannot parse cleaned dataset"),
            (header + "\n", "no rows"),
            ("job_id,skills\nJ1,Python\n", "missing required columns"),
        ]:
            with self.subTest(message=message, contents=contents[:20]):
                self.input.write_text(contents)
                with self.assertRaisesRegex(ValueError, message):
                    self.run_analyzer()
                self.assertFalse(self.output.exists())

    def test_output_directory_failure(self) -> None:
        sample_data().to_csv(self.input, index=False)
        self.output.write_text("Existing file must remain unchanged.")
        with self.assertRaisesRegex(OSError, "Cannot save analysis tables"):
            self.run_analyzer()
        self.assertEqual(self.output.read_text(), "Existing file must remain unchanged.")

    def test_launcher_exit_codes(self) -> None:
        with patch.object(nongraphical_analysis.NonGraphicalAnalyzer, "run") as run, \
             contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(nongraphical_analysis.main(), 0)
            self.assertEqual(errors.getvalue(), "")
            for error in (ValueError("bad data"), FileNotFoundError("no file")):
                with self.subTest(error=type(error).__name__):
                    run.side_effect = error
                    self.assertEqual(nongraphical_analysis.main(), 1)
                    self.assertIn(f"Non-graphical EDA failed: {error}", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
