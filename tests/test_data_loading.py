"""Focused loading, validation, and collection compatibility checks."""

import contextlib
import io
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import (
    load_csv_datasets, validate_required_columns,
    validate_required_datasets, validate_unique_keys,
)
from data_preparation.validation import REQUIRED_DATASETS


class LoadingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in reversed(REQUIRED_DATASETS):
            (self.root / f"{name}.csv").write_text("job_id,value\nJOB001,2\n")

    def test_sorted_sources_extras_and_default_parsing(self):
        (self.root / "extra.csv").write_text("value\n3\n")
        datasets = load_csv_datasets(self.root)
        self.assertEqual(list(datasets), sorted([*REQUIRED_DATASETS, "extra"]))
        for name, frame in datasets.items():
            assert_frame_equal(frame, pd.read_csv(self.root / f"{name}.csv"))
        self.assertEqual(datasets["ai_jobs"].loc[0, "job_id"], "JOB001")

    def test_missing_directory(self):
        with self.assertRaisesRegex(FileNotFoundError, "not found"):
            load_csv_datasets(self.root / "missing")

    def test_missing_sources(self):
        (self.root / "ai_jobs.csv").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "ai_jobs.csv"):
            load_csv_datasets(self.root)

    def test_invalid_csvs_have_path_and_cause(self):
        for content in ("", 'a,b\n1,"unterminated', "a,b\n1,2\n3,4,5\n"):
            with self.subTest(content=content):
                (self.root / "ai_jobs.csv").write_text(content)
                with self.assertRaisesRegex(ValueError, "ai_jobs.csv") as caught:
                    load_csv_datasets(self.root)
                self.assertIsNotNone(caught.exception.__cause__)

    def test_encoding_failure(self):
        (self.root / "ai_jobs.csv").write_bytes(b"value\n\xff\n")
        with self.assertRaisesRegex(ValueError, "ai_jobs.csv") as caught:
            load_csv_datasets(self.root)
        self.assertIsInstance(caught.exception.__cause__, UnicodeError)

    def test_access_failure(self):
        with patch("data_preparation.loading.pd.read_csv", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(OSError, "ai_jobs.csv") as caught:
                load_csv_datasets(self.root)
        self.assertIsInstance(caught.exception.__cause__, PermissionError)


class ValidationTests(unittest.TestCase):
    def test_required_sources(self):
        with self.assertRaisesRegex(ValueError, "skills_demand"):
            validate_required_datasets({name: None for name in REQUIRED_DATASETS[:-1]})

    def test_missing_columns(self):
        with self.assertRaisesRegex(ValueError, "jobs.*job_id"):
            validate_required_columns(pd.DataFrame({"other": []}), "jobs", ["job_id"])

    def test_keys_and_nonmutation(self):
        frame = pd.DataFrame({"country": ["USA", "USA"], "year": [2025, 2026]})
        before = frame.copy(deep=True)
        validate_unique_keys(frame, "trends", ["country", "year"])
        assert_frame_equal(frame, before)
        for invalid in (pd.concat([frame, frame]), frame.assign(year=None)):
            with self.subTest(invalid=invalid.to_dict()):
                with self.assertRaisesRegex(ValueError, "trends.*non-null, unique"):
                    validate_unique_keys(invalid, "trends", ["country", "year"])

    def test_multiple_skills_and_unmatched_jobs(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "01_Data_Collection/data_collection.py"))
        datasets = {
            "ai_jobs": pd.DataFrame({"job_id": ["J1", "J2"], "job_title": ["Analyst"] * 2,
                                     "country": ["USA"] * 2, "posted_year": [2026] * 2}),
            "country_ai_trends": pd.DataFrame({"country": ["USA"], "year": [2026]}),
            "job_title_mapping": pd.DataFrame({"job_title": ["Analyst"]}),
            "skills_demand": pd.DataFrame({"job_id": ["J1", "J1", "J9"],
                                           "skill": ["SQL", "Python", "R"]}),
            "data_dictionary": pd.DataFrame({"description": ["reference"]}),
        }
        before = {name: frame.copy(deep=True) for name, frame in datasets.items()}
        with tempfile.TemporaryDirectory() as temporary:
            namespace["consolidate_data"].__globals__["RAW_DATA_DIR"] = Path(temporary) / "raw"
            with contextlib.redirect_stdout(io.StringIO()):
                result = namespace["consolidate_data"](datasets)
            self.assertEqual(result["job_id"].tolist(), ["J1", "J1", "J2"])
            self.assertTrue(pd.isna(result.loc[2, "skill"]))
            unmatched = pd.read_csv(Path(temporary) / "01_Data_Collection/output/unmatched_skills.csv")
            self.assertEqual(unmatched["job_id"].tolist(), ["J9"])
        for name in datasets:
            assert_frame_equal(datasets[name], before[name])

    def test_collection_checks_columns_before_joining(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "01_Data_Collection/data_collection.py"))
        with self.assertRaisesRegex(ValueError, "ai_jobs.*job_id"):
            namespace["consolidate_data"]({name: pd.DataFrame() for name in REQUIRED_DATASETS})

    def test_imports_from_different_working_directories_without_io(self):
        script = PROJECT_ROOT / "01_Data_Collection/data_collection.py"
        # run_path uses the direct-script import setup without entering __main__.
        code = (
            "import runpy; from unittest.mock import patch; "
            "from pathlib import Path; import pandas as pd; "
            "from contextlib import ExitStack; "
            "stack = ExitStack(); "
            "stack.enter_context(patch.object(pd, 'read_csv', side_effect=AssertionError('read'))); "
            "stack.enter_context(patch.object(Path, 'mkdir', side_effect=AssertionError('mkdir'))); "
            "stack.enter_context(patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('write'))); "
            f"runpy.run_path({str(script)!r}); import data_preparation; stack.close()"
        )
        with tempfile.TemporaryDirectory() as temporary:
            for directory in (PROJECT_ROOT, Path(temporary)):
                result = subprocess.run([sys.executable, "-B", "-c", code], cwd=directory,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
