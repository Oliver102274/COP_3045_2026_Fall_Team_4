# Submission 2, Task 1: Reusable Data Loading and Validation

## Plan First

Review the relevant code and propose a step-by-step implementation plan. Do not modify Python files, run application stages, or implement changes until I explicitly approve the plan.

Keep the implementation appropriate for a Python 2 course. Python 2 is the course name; this application uses Python 3.

## Goal and References

Begin refactoring Nicolas Cava's data preparation work into a reusable package while preserving the first submission's functionality.

Review:

- `01_Data_Collection/data_collection.py`: loading, key validation, joins, exports, and terminal summaries.
- `02_Database/instantiate_database.py`: future consumer of reusable loading; do not refactor it yet.
- `1_database_task.md`, `2_analytical_dataset_task.md`, and `3_data_preparation_task.md`: original task format and data rules.
- `Application/main.py`: current collection invocation.
- `05-Report/reporting/`: existing reusable package example.

## Files After Approval

Create this package at the repository root:

```text
data_preparation/
    __init__.py
    loading.py
    validation.py
```

Update `01_Data_Collection/data_collection.py` to use it. Add focused tests under `tests/` and a short implementation entry in `nicos_devlog.md`.

Explain in the plan how direct script execution will locate the package from both the repository folder and another working directory.

## Requirements

### 1. Reusable Loading

- Extract CSV discovery and reading into `loading.py`, accepting a configurable raw-data directory.
- Preserve sorted CSV discovery and the dictionary of DataFrames keyed by filename stem.
- Require `ai_jobs.csv`, `country_ai_trends.csv`, `data_dictionary.csv`, `job_title_mapping.csv`, and `skills_demand.csv`. Continue loading additional CSVs if present.
- Preserve existing CSV parsing and exact IDs. Do not clean values or guess ID corrections.
- Provide informative errors for missing directories or required files, empty or malformed CSVs, and expected file-access failures. Identify the source path and retain the underlying exception when adding context.

### 2. Reusable Validation

- Add small functions in `validation.py` to validate required dataset names, required columns, and non-null unique keys.
- Check columns used by collection joins before indexing them.
- Preserve unique, non-null key checks for `ai_jobs.job_id`, `job_title_mapping.job_title`, and `(country, year)` in `country_ai_trends`.
- Allow repeated `skills_demand.job_id` values: one job may have several skills.
- Keep `data_dictionary` for reference only.
- Identify the dataset and missing columns or invalid keys in error messages.
- Do not modify input DataFrames during validation.

### 3. Preserve Collection Behavior

- Keep the existing `load_raw_data()` interface as a thin wrapper if needed.
- Replace inline key checks with the reusable functions.
- Preserve existing left joins, merge cardinality checks, country trend prefixes, exact skill matches, and unmatched-skill reporting.
- Preserve one row per job/skill match, including jobs without skills. The later analytical dataset intentionally has a different grain: one row per job.
- Preserve output paths, columns, row order, and terminal inspection and summaries.
- Importing the package or collection script must not read files, create directories, or generate outputs.
- Keep export and inspection logic in the collection script for now.

### 4. Maintainability

- Use clear names, conventional formatting, docstrings, and type hints for new and changed functions.
- Expose a small, clear public interface through `__init__.py`.
- Catch expected exceptions specifically; do not hide programming errors with broad exception handling.
- Leave the meaningful application class for the later cleaning task; no class is needed here.

## Verification After Approval

- Use small fixtures and temporary directories to test loading, discovery order, missing required files, invalid CSVs and file-access failures where practical, missing columns, and invalid keys.
- Verify that repeated skill IDs are accepted and validation does not mutate inputs.
- Compare pre-refactor and post-refactor collection results, including columns, job IDs, missing values, and unmatched skill rows. Route comparison outputs to temporary directories.
- Verify import resolution for direct script launches from the repository and another working directory without running output-generating stages.
- Do not run the full application or overwrite existing CSVs, database, charts, or PDF. State any manual verification left for me.
- Run focused tests in the project environment and accurately report results and limitations.

## Boundaries

Do not change raw data, database scripts, analytical dataset logic, cleaning rules, EDA, reporting, `Application/main.py`, or `environment.yml`. Preserve existing uncommitted edits.

Do not commit, push, or open pull requests without my instruction. You may suggest a feature branch and commit message in the plan.

After implementing and verifying approved changes, append a short dated summary to `nicos_devlog.md` describing the change and validation results. Preserve existing entries.
