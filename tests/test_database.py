"""Database tests use temporary sources and never replace project outputs."""

import contextlib
import io
from pathlib import Path
import runpy
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from pandas.testing import assert_frame_equal
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data_preparation import create_database, read_source_tables
from data_preparation.validation import REQUIRED_DATASETS


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "folder with spaces"
        self.root.mkdir()
        self.raw = self.root / "raw"
        self.raw.mkdir()
        self.database = self.root / "project.db"
        for name in REQUIRED_DATASETS:
            (self.raw / f"{name}.csv").write_text("job_id,value,label\nJ2,2,b\nJ1,,a\n")
        (self.raw / "extra.csv").write_text("value\n9\n")

    def test_round_trip_replacement_and_extra_exclusion(self):
        create_database(self.raw, self.database)
        result = read_source_tables(self.database)
        self.assertEqual(list(result), list(REQUIRED_DATASETS))
        for name, frame in result.items():
            assert_frame_equal(frame, pd.read_csv(self.raw / f"{name}.csv"))
        with contextlib.closing(sqlite3.connect(self.database)) as connection:
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables, set(REQUIRED_DATASETS))
        (self.raw / "ai_jobs.csv").write_text("job_id,value,label\nNEW,4,c\n")
        create_database(self.raw, self.database)
        self.assertEqual(read_source_tables(self.database)["ai_jobs"]["job_id"].tolist(), ["NEW"])

    def test_missing_sources_preserve_existing_database(self):
        create_database(self.raw, self.database)
        before = self.database.read_bytes()
        (self.raw / "ai_jobs.csv").unlink()
        with self.assertRaisesRegex(FileNotFoundError, "ai_jobs.csv"):
            create_database(self.raw, self.database)
        self.assertEqual(self.database.read_bytes(), before)

    def test_missing_output_parent(self):
        with self.assertRaisesRegex(FileNotFoundError, "output directory"):
            create_database(self.raw, self.root / "absent/project.db")
        self.assertFalse((self.root / "absent").exists())

    def test_missing_database_not_created(self):
        with self.assertRaisesRegex(FileNotFoundError, "project.db"):
            read_source_tables(self.database)
        self.assertFalse(self.database.exists())

    def test_invalid_database(self):
        self.database.write_text("not a SQLite database")
        with self.assertRaisesRegex(RuntimeError, "Cannot read database") as caught:
            read_source_tables(self.database)
        self.assertIsInstance(caught.exception.__cause__, SQLAlchemyError)

    def test_missing_tables(self):
        with contextlib.closing(sqlite3.connect(self.database)) as connection:
            connection.execute("CREATE TABLE ai_jobs (job_id TEXT)")
        with self.assertRaisesRegex(ValueError, "missing required tables.*skills_demand"):
            read_source_tables(self.database)

    def test_read_only_and_no_database_changes(self):
        create_database(self.raw, self.database)
        before = self.database.read_bytes()
        original_reader = pd.read_sql_table
        def checking_reader(table, connection):
            with self.assertRaises(SQLAlchemyError):
                connection.execute(text("CREATE TABLE forbidden (value TEXT)"))
            return original_reader(table, connection)
        with patch("data_preparation.database.pd.read_sql_table", side_effect=checking_reader):
            result = read_source_tables(self.database)
        self.assertEqual(self.database.read_bytes(), before)
        self.assertEqual(len(result["ai_jobs"]), 2)

    def test_cleanup_on_write_success_and_failure(self):
        for fail in (False, True):
            with self.subTest(fail=fail):
                engine = create_engine("sqlite://")
                connections = []
                original = pd.DataFrame.to_sql
                def writer(frame, name, connection, **kwargs):
                    connections.append(connection)
                    if fail:
                        raise SQLAlchemyError("simulated write failure")
                    return original(frame, name, connection, **kwargs)
                with patch("data_preparation.database.create_engine", return_value=engine), \
                     patch.object(engine, "dispose", wraps=engine.dispose) as dispose, \
                     patch.object(pd.DataFrame, "to_sql", autospec=True, side_effect=writer):
                    if fail:
                        with self.assertRaisesRegex(RuntimeError, "table ai_jobs") as caught:
                            create_database(self.raw, self.database)
                        self.assertIsInstance(caught.exception.__cause__, SQLAlchemyError)
                    else:
                        create_database(self.raw, self.database)
                    dispose.assert_called_once()
                self.assertTrue(all(connection.closed for connection in connections))

    def test_cleanup_on_connection_failures(self):
        self.database.touch()
        for operation in (lambda: create_database(self.raw, self.database),
                          lambda: read_source_tables(self.database)):
            engine = create_engine("sqlite://")
            with patch("data_preparation.database.create_engine", return_value=engine), \
                 patch.object(engine, "connect", side_effect=SQLAlchemyError("connection denied")), \
                 patch.object(engine, "dispose", wraps=engine.dispose) as dispose:
                with self.assertRaisesRegex(RuntimeError, "project.db"):
                    operation()
                dispose.assert_called_once()

    def test_cleanup_on_read_success_and_failure(self):
        create_database(self.raw, self.database)
        for fail in (False, True):
            disposals = []
            connections = []
            original_reader = pd.read_sql_table
            def engine_factory(url):
                engine = create_engine(url)
                disposal = patch.object(engine, "dispose", wraps=engine.dispose)
                disposals.append(disposal.start())
                self.addCleanup(disposal.stop)
                return engine
            def reader(table, connection):
                connections.append(connection)
                if fail:
                    raise SQLAlchemyError("simulated read failure")
                return original_reader(table, connection)
            with patch("data_preparation.database.create_engine", side_effect=engine_factory), \
                 patch("data_preparation.database.pd.read_sql_table", side_effect=reader):
                if fail:
                    with self.assertRaisesRegex(RuntimeError, "table ai_jobs"):
                        read_source_tables(self.database)
                else:
                    read_source_tables(self.database)
            self.assertTrue(all(connection.closed for connection in connections))
            for disposal in disposals:
                disposal.assert_called_once()
            # File can be renamed after resource cleanup, including on Windows.
            renamed = self.database.with_suffix(".moved")
            self.database.rename(renamed)
            renamed.rename(self.database)

    def test_launcher_failure_status(self):
        namespace = runpy.run_path(str(PROJECT_ROOT / "02_Database/instantiate_database.py"))
        with patch.dict(namespace["main"].__globals__, {"create_database": Mock(side_effect=OSError("denied"))}):
            with contextlib.redirect_stderr(io.StringIO()) as messages:
                self.assertEqual(namespace["main"](), 1)
        self.assertIn("Database creation failed", messages.getvalue())

    def test_imports_without_io_from_other_directories(self):
        for cwd in (PROJECT_ROOT, self.root):
            for script in ("instantiate_database.py", "create_analytical_dataset.py"):
                code = (
                    "import runpy; from unittest.mock import Mock, patch; from contextlib import ExitStack; "
                    "from pathlib import Path; import pandas as pd; import sqlalchemy; "
                    "stack=ExitStack(); "
                    "stack.enter_context(patch.object(pd, 'read_csv', side_effect=AssertionError('read'))); "
                    "stack.enter_context(patch.object(sqlalchemy, 'create_engine', side_effect=AssertionError('database'))); "
                    "stack.enter_context(patch.object(Path, 'mkdir', side_effect=AssertionError('mkdir'))); "
                    "stack.enter_context(patch.object(pd.DataFrame, 'to_csv', side_effect=AssertionError('write'))); "
                    f"runpy.run_path({str(PROJECT_ROOT / '02_Database' / script)!r}); stack.close()"
                )
                result = subprocess.run([sys.executable, "-B", "-c", code], cwd=cwd, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
