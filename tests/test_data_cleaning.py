"""DataCleaner tests use temporary files and synthetic string-valued data."""

import contextlib
import io
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from pandas.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from data_preparation import DataCleaner #noqa: E402


def sample_data(count=3):
    """Return a complete string-valued cleaning input with optional extra fields."""
    return pd.DataFrame({
        "job_id": [f"J{i}" for i in range(count)],
        "job_title": ["Data Analyst"] * count,
        "country": ["USA"] * count,
        "experience_level": ["Entry"] * count,
        "remote_type": ["Remote"] * count,
        "salary_min_usd": ["100"] * count,
        "salary_max_usd": ["200"] * count,
        "min_experience_years": ["0"] * count,
        "posted_year": ["2026"] * count,
        "country_total_ai_jobs": ["1000"] * count,
        "country_avg_salary_usd": ["150"] * count,
        "country_remote_percentage": ["50"] * count,
        "skills": [None] * count,
        "extra": [" unchanged "] * count,
    }, dtype="string")


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.input = self.root / "input.csv"
        self.output = self.root / "output.csv"
        self.cleaner = DataCleaner(self.input, self.output)

    def clean(self, data):
        with contextlib.redirect_stdout(io.StringIO()):
            return self.cleaner.clean_dataframe(data)

    def test_duplicates_ids_order_and_input_unchanged(self):
        data = sample_data()
        data.loc[0, "job_id"] = " J0 "
        data = pd.concat([data, data.iloc[:1]])
        before = data.copy(deep=True)
        result = self.clean(data)
        assert_frame_equal(data, before)
        self.assertEqual(result.index.tolist(), [0, 1, 2])
        self.assertEqual(result["job_id"].tolist(), [" J0 ", "J1", "J2"])
        self.assertEqual(result.columns.tolist(), data.columns.tolist())
        self.assertEqual(result["extra"].tolist(), [" unchanged "] * 3)

    def test_invalid_ids_and_existing_output_preserved(self):
        for invalid in (None, "   ", "J1"):
            with self.subTest(invalid=invalid):
                data = sample_data()
                data.loc[0, "job_id"] = invalid
                data.loc[0, "salary_min_usd"] = "99"
                data.to_csv(self.input, index=False)
                self.output.write_text("existing output")
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, "job IDs"):
                    self.cleaner.run()
                self.assertEqual(self.output.read_text(), "existing output")

    def test_text_labels_and_missingness(self):
        data = sample_data()
        data["remote_type"] = pd.Series([" remote ", "HYBRID", " onsite "], dtype="string")
        data.loc[0, "job_title"] = " data analyst "
        data.loc[0, "country"] = " usa "
        data.loc[0, "experience_level"] = " entry "
        data.loc[1, "job_title"] = " New Role "
        data.loc[2, "extra"] = "   "
        result = self.clean(data)
        self.assertEqual(result["remote_type"].tolist(), ["Remote", "Hybrid", "Onsite"])
        self.assertEqual(result.loc[0, "job_title"], "Data Analyst")
        self.assertEqual(result.loc[1, "job_title"], "New Role")
        self.assertEqual(result.loc[0, "country"], "USA")
        self.assertEqual(result.loc[0, "experience_level"], "Entry")
        self.assertTrue(pd.isna(result.loc[2, "extra"]))
        self.assertTrue(result["skills"].isna().all())

    def test_numeric_rules_and_nullable_types(self):
        data = sample_data(6)
        data["salary_min_usd"] = pd.Series(["-1", "300", "-1", "bad", "inf", None], dtype="string")
        data["salary_max_usd"] = pd.Series(["200", "200", "-2", "-inf", "200", None], dtype="string")
        data["min_experience_years"] = pd.Series(["-1", "0", "bad", "inf", "2", None], dtype="string")
        result = self.clean(data)
        self.assertTrue(result["salary_min_usd"].isna().all())
        self.assertEqual(result.loc[0, "salary_max_usd"], 200)
        self.assertTrue(result.loc[1:3, "salary_max_usd"].isna().all())
        self.assertEqual(result.loc[1, "min_experience_years"], 0)
        self.assertTrue(result.loc[[0, 2, 3, 5], "min_experience_years"].isna().all())
        for column in ("salary_min_usd", "salary_max_usd", "min_experience_years", "country_total_ai_jobs", "country_avg_salary_usd", "country_remote_percentage"):
            self.assertEqual(str(result[column].dtype), "Float64")

    def test_year_boundaries(self):
        data = sample_data(7)
        data["posted_year"] = pd.Series(["2020", "2026", "2019", "2027", "2025.5", None, "bad"], dtype="string")
        result = self.clean(data)
        self.assertEqual(result["posted_year"].iloc[:2].tolist(), [2020, 2026])
        self.assertTrue(result["posted_year"].iloc[2:].isna().all())
        self.assertEqual(str(result["posted_year"].dtype), "Int64")

    def test_required_columns_and_dtype_expectations(self):
        with self.assertRaisesRegex(ValueError, "cleaning input.*posted_year"):
            self.clean(sample_data().drop(columns="posted_year"))
        data = sample_data()
        data["salary_min_usd"] = [1, 2, 3]
        with self.assertRaisesRegex(ValueError, "salary_min_usd.*string dtype"):
            self.clean(data)

    def test_repeated_calls_and_empty_data(self):
        data = sample_data()
        first = self.clean(data)
        assert_frame_equal(first, self.clean(data))
        self.assertEqual(len(self.clean(data.iloc[:1])), 1)
        self.assertTrue(self.clean(data.iloc[:0]).empty)

    def test_successful_file_run(self):
        sample_data().to_csv(self.input, index=False)
        before = self.input.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            result = self.cleaner.run()
        self.assertEqual(self.input.read_bytes(), before)
        self.assertEqual(self.output.read_bytes(), result.to_csv(index=False).encode("utf-8"))
        self.assertEqual(pd.read_csv(self.output).columns.tolist(), result.columns.tolist())

    def test_missing_and_invalid_input(self):
        with self.assertRaisesRegex(OSError, "input.csv"):
            self.cleaner.run()
        for content in ("", 'a,b\n1,"unfinished'):
            self.input.write_text(content)
            with self.assertRaisesRegex(ValueError, "Cannot parse.*input.csv") as caught:
                self.cleaner.run()
            self.assertIsNotNone(caught.exception.__cause__)

    def test_same_paths_and_output_failures(self):
        sample_data().to_csv(self.input, index=False)
        with self.assertRaisesRegex(ValueError, "must be different"):
            DataCleaner(self.input, self.root / "./input.csv").run()
        with contextlib.redirect_stdout(io.StringIO()), patch.object(pd.DataFrame, "to_csv", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(OSError, "Cannot save.*output.csv") as caught:
                self.cleaner.run()
        self.assertIsInstance(caught.exception.__cause__, PermissionError)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(OSError, "Cannot save"):
            DataCleaner(self.input, self.root / "missing/output.csv").run()
        self.assertFalse((self.root / "missing").exists())

    def test_constructor_and_imports_have_no_io(self):
        with patch.object(pd, "read_csv", side_effect=AssertionError("read")), patch.object(Path, "mkdir", side_effect=AssertionError("mkdir")):
            DataCleaner(self.input, self.output)
        script = PROJECT_ROOT / "03_Data_Cleaning/clean_data.py"
        code = (
            "import runpy; from unittest.mock import patch; from contextlib import ExitStack; "
            "from pathlib import Path; import pandas as pd; import sqlalchemy; stack=ExitStack(); "
            "stack.enter_context(patch.object(pd,'read_csv',side_effect=AssertionError('read'))); "
            "stack.enter_context(patch.object(Path,'mkdir',side_effect=AssertionError('mkdir'))); "
            "stack.enter_context(patch.object(pd.DataFrame,'to_csv',side_effect=AssertionError('write'))); "
            "stack.enter_context(patch.object(sqlalchemy,'create_engine',side_effect=AssertionError('database'))); "
            f"runpy.run_path({str(script)!r}); from data_preparation import DataCleaner; DataCleaner('in','out'); stack.close()"
        )
        for cwd in (PROJECT_ROOT, self.root):
            result = subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_launcher_failure_status(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "03_Data_Cleaning/clean_data.py"))
        cleaner = Mock()
        cleaner.return_value.run.side_effect = ValueError("bad input")
        with patch.dict(namespace["main"].__globals__, {"DataCleaner": cleaner}), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(namespace["main"](), 1)
        self.assertIn("Data cleaning failed", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
