# Submission 2, Task 2: Reusable Database Operations

## Plan First

Review the relevant code and propose a step-by-step implementation plan. Do not modify Python files, execute application stages, or implement changes until I explicitly approve the plan.

Keep the code appropriate for a Python 2 course. Python 2 is the course name; the application uses Python 3.

## Goal and References

Refactor Nicolas Cava's database creation and table-reading code into reusable functions within the existing `data_preparation` package. Preserve the five source tables and the analytical dataset's behavior.

Review:

- `02_Database/instantiate_database.py`: current CSV loading and SQLite creation.
- `02_Database/create_analytical_dataset.py`: current read-only table loading and analytical workflow.
- `data_preparation/loading.py`, `validation.py`, and `__init__.py`: reusable functions from Task 1.
- `01_Data_Collection/data_collection.py`: package import setup for direct execution.
- `tasks/submission1/1_database_task.md` and `tasks/submission1/2_analytical_dataset_task.md`: original database requirements.
- `Application/main.py`: existing stage invocation and failure handling.
- `tests/test_data_loading.py`: existing data preparation tests.

## Files After Approval

- Create `data_preparation/database.py`.
- Update `data_preparation/__init__.py` to expose the new public functions.
- Refactor `02_Database/instantiate_database.py` into a small launcher with `main()` and an execution guard.
- Update only the database loading and resource-management portions of `02_Database/create_analytical_dataset.py` to use the reusable reader.
- Add `tests/test_database.py` and a short implementation entry in `nicos_devlog.md`.

## Requirements

### 1. Reusable Database Creation

- Provide a function accepting a raw-data directory and a database path.
- Reuse `load_csv_datasets()` instead of repeating the five `pd.read_csv()` calls.
- Load and validate required dataset names before opening the output database, so missing or unreadable CSVs do not initiate database replacement.
- Write exactly these source tables: `ai_jobs`, `country_ai_trends`, `data_dictionary`, `job_title_mapping`, and `skills_demand`. The loader may return extra datasets; do not write them as additional tables.
- Preserve `to_sql(if_exists="replace", index=False)`, source values, columns, and row order. Do not clean values or add analytical columns.
- Preserve the default output `02_Database/project.db` and portable SQLAlchemy SQLite URLs.
- Use context managers and `finally` where appropriate so connections close and engines are disposed even if connecting or writing fails.
- Use a transaction for writes, but do not claim that SQLite table replacement is fully atomic unless verified. Do not add a backup or temporary-database replacement system in this task.

### 2. Reusable Read-Only Table Loading

- Provide a function accepting a database path and returning the five source DataFrames in a dictionary keyed by table name.
- Require an existing file before connecting; a missing database must not be silently created.
- Preserve the existing SQLite read-only connection behavior and `pd.read_sql_table()` parsing.
- Validate that required tables exist and report missing table names clearly.
- Keep `data_dictionary` available for reference; do not join it to job records.
- Close connections and dispose engines on success and expected failures. Return usable DataFrames after resources have closed.

### 3. Integrate Existing Scripts

- Give database creation a typed, documented `main()` coordinating the reusable function.
- Replace the analytical script's database setup, table reads, and connection cleanup with the new reader, retaining the existing DataFrame variable names where useful.
- Leave analytical key checks, joins, skills summaries, coverage messages, job-preservation checks, CSV writing, and output paths unchanged. Refactoring those operations belongs to Task 3.
- Dedenting the analytical workflow after removing the connection block is allowed; do not otherwise reorganize its logic.
- Resolve the package from each script's location so direct launches work from any working directory.
- Keep required package imports after path setup; use a targeted `# noqa: E402` if needed to document this intentional Ruff exception.
- Importing the package or either script must not load data, open databases, create directories, or generate outputs.
- Expected creation failures must produce an informative message and a nonzero exit status so `Application/main.py` stops. Analytical read failures must also propagate as failures, never be converted into successful empty results.

### 4. Validation and Readability

- Use clear names, docstrings, and type hints for new and changed functions.
- Include the database path and table name where relevant in expected error messages; retain underlying exceptions when adding context.
- Handle expected filesystem and SQLAlchemy exceptions specifically. Do not catch all exceptions or suppress programming errors.
- Report a missing output parent directory clearly rather than silently creating a new project folder structure.
- Reuse Task 1 validation where appropriate without introducing stricter data-cleaning rules.
- No class or new dependency is needed for this task.

## Verification After Approval

- Use temporary folders, small source CSV fixtures, and temporary SQLite databases for focused tests.
- Check all five tables, column names, row order, values, missing values, and absence of an exported DataFrame index.
- Verify replacement on a second run and that extra CSVs are not written as source tables.
- Test missing source files, missing output directories, missing databases, invalid database files, missing tables, and simulated access or write failures where practical.
- Verify that missing input CSVs do not alter an existing database.
- Confirm read-only loading does not modify the database and supports paths containing spaces.
- Verify cleanup after success and failures, including a failed connection or table write.
- Verify imports from the repository and a different working directory without executing output-generating stages.
- Compare old and refactored creation and reading behavior using the included data and temporary database copies. Compare analytical CSV results in temporary folders if needed to validate the reader integration.
- Run the focused database tests and existing Task 1 tests in `cop3045`; report commands, results, and any remaining manual checks.
- Do not run the full application or overwrite the existing project database, CSVs, charts, or PDF.

## Boundaries and Devlog

Do not change raw data, collection behavior, analytical calculations or joins, cleaning, EDA, reporting, `Application/main.py`, or `environment.yml`. Preserve existing uncommitted edits.

Do not commit, push, or open pull requests without my instruction. The plan may suggest a feature branch and commit message.

After implementing and verifying approved changes, append a short dated summary to `nicos_devlog.md` describing what changed and validation results. Preserve existing entries.
