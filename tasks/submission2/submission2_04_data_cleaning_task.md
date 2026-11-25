# Submission 2, Task 4: Data Cleaning with a DataCleaner Class

## Plan First

Review the relevant code and propose a step-by-step implementation plan. Do not modify Python files, execute application stages, or implement changes until I explicitly approve the plan.

Keep the implementation appropriate for a Python 2 course. Python 2 is the course name; this project uses Python 3.

## Goal and References

Refactor Nicolas Cava's existing cleaning workflow into a meaningful `DataCleaner` class within `data_preparation`. Demonstrate a constructor, instance methods, and encapsulation while preserving the existing cleaning rules and cleaned CSV consumed by EDA and reporting.

Review:

- `03_Data_Cleaning/clean_data.py`: source of truth for current cleaning rules, their order, and terminal summaries.
- `tasks/submission1/3_data_preparation_task.md`: original cleaning requirements.
- `data_preparation/validation.py` and `__init__.py`: reusable validation and package interface.
- `02_Database/create_analytical_dataset.py`: upstream CSV and launcher conventions.
- `Application/main.py`: current cleaning stage invocation and failure handling.
- `04_EDA/nongraphical_analysis.py`, `04_EDA/eda_analysis.py`, and `05-Report/reporting/analysis.py`: downstream column expectations; do not modify them.
- Existing data preparation tests and `05-Report/reporting/report.py`: test conventions and an existing meaningful class example.

## Files After Approval

- Create `data_preparation/cleaning.py` with `DataCleaner`.
- Expose `DataCleaner` through `data_preparation/__init__.py`.
- Refactor `03_Data_Cleaning/clean_data.py` into a small launcher with a typed, documented `main()` and an execution guard.
- Add `tests/test_data_cleaning.py`.
- Append a short implementation entry to `nicos_devlog.md`.

Reuse existing validation helpers where appropriate. Only extend them if the approved plan establishes a clear need.

## Requirements

### 1. Meaningful Object-Oriented Design

- Give `DataCleaner` an `__init__` that stores input and output paths as internal attributes, using the underscore convention for encapsulation.
- Construction must not read files, create directories, or write outputs.
- Provide a public instance method that coordinates loading, inspection, cleaning, validation, reporting, and saving, and returns the cleaned DataFrame on success.
- Provide a reusable method for cleaning a supplied DataFrame without file reads or writes. Define and document its input expectations; preserve the file workflow's string-based parsing semantics.
- Copy supplied data so cleaning does not mutate a caller's DataFrame.
- Split substantial operations into clearly named instance methods, such as duplicate/ID handling, text normalization, numeric conversion, invalid-value handling, and summaries. Keep the number of methods practical.
- Avoid unnecessary inheritance, property methods, custom exception hierarchies, or configuration frameworks.
- Add docstrings and type hints to the class constructor and methods. Explain that underscore attributes/methods are internal by Python convention.

### 2. Preserve Input and Duplicate Handling

- Load the analytical CSV with `dtype="string"`, preserving exact IDs and allowing numeric conversion failures to be identified.
- Validate all columns accessed by cleaning before indexing them, using informative missing-column messages. Keep additional columns and their order.
- Remove only exact duplicate rows before checking IDs; preserve retained row order and existing index behavior.
- Reject null or whitespace-only job IDs and conflicting duplicate IDs after exact deduplication. Preserve exact nonblank IDs rather than trimming or correcting them.
- Preserve the current diagnostic counts and example IDs for invalid inputs.
- Do not save when validation fails; an existing cleaned CSV must remain untouched on input or cleaning validation failures.

### 3. Preserve Text and Missing-Value Rules

- Convert whitespace-only non-ID fields to missing without broadly trimming every field.
- Trim and normalize known labels only in `job_title`, `country`, `experience_level`, and `remote_type`, using the existing canonical labels and case-insensitive mapping.
- Retain unknown labels after trimming and report them for review.
- Keep Remote, Hybrid, and Onsite distinct.
- Retain jobs with missing skills, country trends, salaries, or experience. Do not fill those values with zero or averages.
- Missing skills must not be interpreted as no skills required.

### 4. Preserve Numeric and Year Rules in Their Existing Order

- Convert the existing seven numeric columns with coercion and nullable `Float64`: salary bounds, minimum experience, posting year, and the three country trend numeric fields.
- Report unconvertible and infinite values; set infinities to missing.
- Identify reversed salary ranges before masking negative salaries, preserving the current overlap behavior.
- Mask negative salary bounds and set both bounds to missing for reversed ranges.
- Mask negative minimum experience; retain zero.
- Validate posting years as whole numbers from 2020 through 2026 inclusive. Set invalid years to missing and return `posted_year` as nullable `Int64`.
- Do not replace 2026 with the current system year or introduce new country statistic range rules during this refactor.
- Leave derived values, filtering, summaries for EDA, charts, and PDF generation to their existing stages.

### 5. Launcher, Output, and Errors

- Preserve default input `02_Database/consolidated_data_database.csv` and output `03_Data_Cleaning/clean_data.csv`.
- Preserve output values, missingness, column and row order, nullable types in memory, and `index=False` CSV export.
- Preserve before/after inspection, invalid-value counts, missing-value summaries, and saved-path messages where practical. Do not substitute hard-coded results.
- Resolve package imports relative to the script location so direct execution works from any working directory. Use a targeted `# noqa: E402` for the intentional package import after path setup.
- Importing the package or launcher must not read files, connect to databases, create directories, or generate outputs.
- Give expected missing-file, parsing, validation, and output-access failures informative context and a nonzero launcher exit status. Retain causes when adding context and catch expected exception types rather than all exceptions.
- Do not create missing output directories or write to the input file. Reject explicitly identical input/output paths to prevent accidental source replacement.
- Do not promise atomic recovery from a mid-write output failure; that is outside this task.

## Verification After Approval

- Preserve a temporary baseline of the original cleaning script before editing.
- Use small synthetic fixtures and temporary files for tests; do not overwrite existing project outputs.
- Cover exact duplicates, conflicting IDs, null/blank IDs, exact ID preservation, whitespace-only fields, canonical/unknown labels, and distinct work arrangements.
- Cover missing values, nonnumeric and infinite values, negative salaries, reversed ranges including overlaps with negatives, negative experience, and valid zero experience.
- Cover years at both valid boundaries, outside the range, fractional years, and missing years; verify nullable numeric dtypes.
- Verify required-column errors, preservation of extra columns and row order, unchanged input DataFrames, and repeated use of an instance without stale counts or results.
- Test missing/invalid CSV input, identical input/output paths, output failures, and preservation of an existing output after validation failure.
- Check constructor/import behavior without file access and package resolution from the repository and another working directory without executing project stages.
- Compare original and refactored cleaning using the included analytical CSV and temporary destinations: check values, missingness, dtypes, row/column order, diagnostic counts/messages, and CSV bytes. Compare representative dirty fixtures as well so unchanged behavior is verified beyond the current data.
- Run the new cleaning tests and existing Task 1-3 tests in `cop3045`; report commands, actual results, and remaining manual verification.
- Do not run the full application or regenerate the project database, existing CSVs, charts, or PDF.

## Boundaries and Devlog

Do not change raw data, collection, database operations, analytical dataset logic, EDA, reporting, `Application/main.py`, or `environment.yml`. Preserve existing uncommitted edits.

No new dependency is needed. This task supplies a meaningful class for Nicolas's data preparation contribution.

Do not commit, push, or open pull requests without my instruction. The plan may suggest a feature branch and commit message.

After implementing and verifying approved changes, append a short dated summary to `nicos_devlog.md` describing the change and validation results. Preserve existing entries.
