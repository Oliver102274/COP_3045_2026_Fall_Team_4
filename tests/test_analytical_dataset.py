"""Analytical construction and launcher checks without project output writes."""

import contextlib
import io
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from pandas.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import (
    build_analytical_dataset, calculate_skill_coverage, print_skill_coverage,
    summarize_skills, validate_job_preservation,
)


def sources():
    """Provide unsorted jobs, lookup gaps, repeated skills, and exact-ID misses."""
    return {
        "ai_jobs": pd.DataFrame({
            "job_id": ["J2", "J1", "J3", "J4"],
            "job_title": ["Analyst", "Analyst", "Unknown", "Analyst"],
            "country": ["USA", "USA", "UK", "USA"],
            "posted_year": [2026, 2025, 2026, 2026],
            "salary_min_usd": [1.0, 2.0, None, 4.0],
        }),
        "job_title_mapping": pd.DataFrame({"job_title": ["Analyst"], "standardized_title": ["Data Analyst"]}),
        "country_ai_trends": pd.DataFrame({"country": ["USA", "USA"], "year": [2025, 2026], "total_ai_jobs": [10, 20]}),
        "skills_demand": pd.DataFrame({
            "job_id": ["J2", "J2", "J2", "J1", "J9", "J9", None, " J3"],
            "skill": ["SQL", "Python", "SQL", None, "R", "R", "SQL", "SQL"],
        }),
        "data_dictionary": pd.DataFrame({"description": ["reference only"]}),
    }


class AnalyticalTests(unittest.TestCase):
    def test_join_values_order_missing_matches_and_nonmutation(self):
        datasets = sources()
        before = {name: frame.copy(deep=True) for name, frame in datasets.items()}
        result = build_analytical_dataset(datasets)
        self.assertEqual(result["job_id"].tolist(), ["J2", "J1", "J3", "J4"])
        assert_frame_equal(result[list(datasets["ai_jobs"].columns)], datasets["ai_jobs"])
        self.assertEqual(result.columns.tolist(), [*datasets["ai_jobs"].columns, "standardized_title", "country_total_ai_jobs", "skills"])
        self.assertEqual(result.loc[0, "skills"], "Python; SQL")
        self.assertTrue(result.loc[1:, "skills"].isna().all())
        self.assertTrue(pd.isna(result.loc[2, "standardized_title"]))
        self.assertTrue(pd.isna(result.loc[2, "country_total_ai_jobs"]))
        self.assertEqual(result.loc[:1, "country_total_ai_jobs"].tolist(), [20.0, 10.0])
        for name in datasets:
            assert_frame_equal(datasets[name], before[name])

    def test_skill_summary(self):
        data = sources()
        summary = summarize_skills(data["ai_jobs"], data["skills_demand"])
        self.assertEqual(summary.to_dict("records"), [{"job_id": "J2", "skills": "Python; SQL"}])

    def test_coverage_and_messages(self):
        data = sources()
        metrics = calculate_skill_coverage(data["ai_jobs"], data["skills_demand"])
        self.assertEqual(metrics, {
            "unmatched_skill_rows": 4, "distinct_unmatched_skill_ids": 2,
            "jobs_without_skills": 2, "matched_jobs": 2, "total_jobs": 4, "coverage": 0.5,
        })
        with contextlib.redirect_stdout(io.StringIO()) as output:
            print_skill_coverage(metrics)
        self.assertIn("Skill ID coverage: 2/4 jobs (50.0%)", output.getvalue())
        self.assertIn("Missing skill matches do not mean no skills are required.", output.getvalue())

    def test_missing_datasets_and_columns(self):
        data = sources()
        del data["data_dictionary"]
        with self.assertRaisesRegex(ValueError, "data_dictionary"):
            build_analytical_dataset(data)
        for name, column in (("ai_jobs", "posted_year"), ("skills_demand", "skill"),
                             ("job_title_mapping", "job_title"), ("country_ai_trends", "year")):
            with self.subTest(name=name):
                data = sources()
                data[name] = data[name].drop(columns=column)
                with self.assertRaisesRegex(ValueError, f"{name}.*{column}"):
                    build_analytical_dataset(data)

    def test_null_and_duplicate_keys(self):
        for name, column in (("ai_jobs", "job_id"), ("job_title_mapping", "job_title"),
                             ("country_ai_trends", "year")):
            for problem in ("null", "duplicate"):
                with self.subTest(name=name, problem=problem):
                    data = sources()
                    if problem == "null":
                        data[name].loc[0, column] = None
                    else:
                        data[name] = pd.concat([data[name], data[name].iloc[:1]], ignore_index=True)
                    with self.assertRaisesRegex(ValueError, f"{name}.*non-null, unique"):
                        build_analytical_dataset(data)

    def test_job_preservation_failures(self):
        jobs = sources()["ai_jobs"]
        for result in (jobs.iloc[:-1], jobs.assign(job_id=["J2", "J2", "J3", "J4"]),
                       jobs.assign(job_id=["J2", "J1", None, "J4"]),
                       jobs.assign(job_id=["J2", "J1", "OTHER", "J4"])):
            with self.assertRaisesRegex(ValueError, "every job exactly once"):
                validate_job_preservation(jobs, result)

    def test_empty_jobs_and_skills(self):
        data = sources()
        data["ai_jobs"] = data["ai_jobs"].iloc[:0]
        result = build_analytical_dataset(data)
        self.assertTrue(result.empty)
        metrics = calculate_skill_coverage(data["ai_jobs"], data["skills_demand"])
        self.assertEqual(metrics["coverage"], 0.0)
        self.assertEqual(metrics["unmatched_skill_rows"], 8)
        data = {name: frame.iloc[:0] for name, frame in sources().items()}
        self.assertTrue(build_analytical_dataset(data).empty)
        data = sources()
        data["skills_demand"] = data["skills_demand"].iloc[:0]
        self.assertTrue(build_analytical_dataset(data)["skills"].isna().all())

    def test_launcher_success_without_file_writes(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "02_Database/create_analytical_dataset.py"))
        with patch.dict(namespace["main"].__globals__, {"read_source_tables": Mock(return_value=sources())}), \
             patch.object(pd.DataFrame, "to_csv") as save, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(namespace["main"](), 0)
            save.assert_called_once_with(PROJECT_ROOT / "02_Database/consolidated_data_database.csv", index=False)

    def test_launcher_input_and_output_failures(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "02_Database/create_analytical_dataset.py"))
        for error in (FileNotFoundError("missing database"), ValueError("bad source"), RuntimeError("database read failed")):
            with patch.dict(namespace["main"].__globals__, {"read_source_tables": Mock(side_effect=error)}), \
                 patch.object(pd.DataFrame, "to_csv") as save, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(namespace["main"](), 1)
                save.assert_not_called()
        with patch.dict(namespace["main"].__globals__, {"read_source_tables": Mock(return_value=sources())}), \
             patch.object(pd.DataFrame, "to_csv", side_effect=PermissionError("denied")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(namespace["main"](), 1)
        self.assertIn("Cannot save analytical dataset to", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
