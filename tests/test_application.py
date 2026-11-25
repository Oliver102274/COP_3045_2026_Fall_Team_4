"""Entry-point checks mock subprocesses and never run application stages."""

import contextlib
import io
from pathlib import Path
import runpy
import subprocess
import unittest
from unittest.mock import patch


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "Application/main.py"))
        self.main = self.module["main"]

    def test_failed_stage_stops_later_stages(self):
        for error in (subprocess.CalledProcessError(1, "stage"), OSError("cannot launch")):
            with self.subTest(error=type(error).__name__), \
                 patch.object(subprocess, "run", side_effect=[None, error]) as run, \
                 contextlib.redirect_stdout(io.StringIO()) as output, \
                 contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(self.main(), 1)
                self.assertEqual(run.call_count, 2)
                self.assertIn("Database creation failed", errors.getvalue())
                self.assertNotIn("Workflow complete", output.getvalue())

    def test_missing_final_report_is_failure(self):
        with patch.object(subprocess, "run") as run, \
             patch.object(Path, "is_file", return_value=False), \
             contextlib.redirect_stdout(io.StringIO()) as output, \
             contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(self.main(), 1)
            self.assertEqual(run.call_count, 7)
            self.assertIn("No PDF report was generated", errors.getvalue())
            self.assertNotIn("Workflow complete", output.getvalue())


if __name__ == "__main__":
    unittest.main()
