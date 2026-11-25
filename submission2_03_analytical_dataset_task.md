# Submission 2, Task 3: Reusable Analytical Dataset Creation

## Plan First

Review the relevant code and propose a step-by-step implementation plan. Do not modify Python files, run application stages, or implement changes until I explicitly approve the plan.

Keep the code appropriate for a Python 2 course. Python 2 is the course name; the application uses Python 3.

## Goal and References

Refactor Nicolas Cava's analytical dataset workflow into reusable functions in the existing `data_preparation` package. Preserve one row per job, exact skill matching, and the existing analytical CSV.

Review:

- `02_Database/create_analytical_dataset.py`: current joins, skills summary, coverage reporting, validation, and export.
- `data_preparation/database.py`: reusable read-only table loading from Task 2.
- `data_preparation/validation.py` and `__init__.py`: existing checks and public interface.
- `2_analytical_dataset_task.md`: original analytical requirements.
- `01_Data_Collection/data_collection.py`: intentionally different job/skill row structure; do not change it.
- `03_Data_Cleaning/clean_data.py`: downstream analytical CSV consumer; do not change it.
- `Application/main.py` and existing data preparation tests: invocation and compatibility expectations.

## Files After Approval

- Create `data_preparation/analytical.py`.
- Update `data_preparation/__init__.py` to expose the necessary public functions.
- Refactor `02_Database/create_analytical_dataset.py` into a small launcher with a documented, typed `main()` and an execution guard.
- Add `tests/test_analytical_dataset.py`.
- Append a short implementation entry to `nicos_devlog.md`.

Reuse existing validation helpers. Only extend `validation.py` if the approved plan identifies a clear need; avoid duplicating checks.

## Requirements

### 1. Separate Responsibilities

- Provide a function that builds the analytical DataFrame from a dictionary of source DataFrames without reading or writing files.
- Extract skills summarization, coverage calculation/reporting, and final job-preservation validation into small functions with clear responsibilities where useful.
- Keep coverage calculations testable separately from terminal printing. Use a simple documented return structure for metrics; avoid unnecessary abstractions or classes.
- Let the launcher coordinate read-only database loading, analytical construction, terminal reporting, and CSV export.
- Add clear names, docstrings, and type hints to new and changed functions.
- Do not mutate source DataFrames.

### 2. Validate Sources Before Joining

- Require the existing five source datasets, including the reference-only `data_dictionary`.
- Validate required columns before accessing them. Include join keys and `skills_demand.skill`; keep additional source columns.
- Reuse checks for non-null, unique `ai_jobs.job_id`, `job_title_mapping.job_title`, and `(country, year)` in `country_ai_trends`.
- Allow repeated skill job IDs and duplicate skill names, which are summarized later.
- Identify the source dataset and missing columns or invalid keys in errors.
- Do not introduce cleaning, whitespace normalization, guessed ID corrections, or stricter analytical policies during this refactor.

### 3. Preserve Analytical Construction

- Start from jobs and left join title mappings on `job_title` with `validate="many_to_one"`.
- Left join country trends using `country` and `posted_year` matched to `year`, preserving existing `country_` prefixes and avoiding duplicated join-key columns.
- Match skills using exact `job_id` values only. Exclude unmatched skill records from the job-level summary.
- Drop missing skill names before aggregation. Combine sorted unique names using the existing `"; "` separator.
- Left join summarized skills with `validate="one_to_one"` so all jobs remain, including those without matching or usable skills.
- Preserve every original job column and the existing output column and row order.
- Keep `data_dictionary` for reference only; do not merge it into jobs.
- Verify the output retains all original job IDs exactly once, with unchanged job count and no missing or duplicated output IDs.
- Leave derived values, current-year filtering, cleaning, statistics, charts, and PDF generation to their existing stages.

### 4. Preserve Coverage Meaning

- Preserve counts of unmatched skill rows, distinct unmatched skill IDs, jobs without matching skill records, matched jobs, total jobs, and the coverage percentage.
- Preserve the current distinction between a matching skill record and a usable skill name: a matched row with a missing skill name still counts toward ID coverage.
- Preserve the current `nunique()` handling of missing unmatched IDs and the zero-denominator rule for empty jobs.
- Preserve terminal wording and percentage formatting where practical, including the limitation that missing skill matches do not mean no skills are required.
- Calculate metrics from inputs rather than hard-coding known dataset counts.

### 5. Launcher and Failures

- Use `read_source_tables()` from Task 2 and preserve the default paths `02_Database/project.db` and `02_Database/consolidated_data_database.csv`.
- Save with `index=False` only after construction and validation succeed.
- Preserve the analytical dimensions and saved-path messages.
- Resolve package imports relative to the script location, supporting direct execution from another working directory. Keep a targeted `# noqa: E402` for the intentional import after path setup.
- Importing the package or script must not read sources, connect to databases, create directories, or generate outputs.
- Give expected input, merge, database, and output failures informative context and a nonzero exit status so the application stops. Catch specific expected exceptions without hiding programming errors, and preserve causes when adding context.
- Do not create new output directories or change database tables.

## Verification After Approval

- Use small synthetic DataFrames covering multiple jobs sharing a title, multiple country/year records, missing lookup matches, repeated and unsorted skill names, unmatched skill IDs, missing skill names, and jobs without skills.
- Verify exact ID matching, sorted unique skill strings, country prefixes, preserved row order and original job columns, and one row per original job.
- Cover missing datasets or columns, null or duplicate source keys, and final job-preservation failures.
- Verify coverage metrics separately, including matching records with missing skill names, unmatched missing IDs, and correctly shaped empty inputs.
- Confirm input frames remain unchanged.
- Test launcher failure status and simulated CSV output errors using temporary destinations or mocks.
- Verify imports and package resolution from the repository and another working directory without running output-generating stages.
- Preserve a temporary baseline before editing. Compare the original and refactored workflow using the included database and temporary CSV destinations, checking DataFrame values, missing values, columns, row order, coverage metrics/messages, and exported CSV content. The current baseline is 50,000 rows and 21 columns; do not hard-code those counts into production logic.
- Run new analytical tests and existing Task 1/2 tests in `cop3045`; report commands, actual results, and remaining manual verification.
- Do not run the full application or overwrite existing project CSVs, database, charts, or PDF.

## Boundaries and Devlog

Do not change raw data, collection, database creation or reading behavior, cleaning, EDA, reporting, `Application/main.py`, or `environment.yml`. Preserve existing uncommitted edits.

No class or new dependency is needed. The meaningful application class remains planned for the data cleaning task.

Do not commit, push, or open pull requests without my instruction. You may suggest a feature branch and commit message in the plan.

After implementing and verifying approved changes, append a short dated summary to `nicos_devlog.md` describing the change and validation results. Preserve existing entries.
