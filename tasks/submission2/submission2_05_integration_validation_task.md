# Submission 2, Task 5: Integration, Validation, and Documentation

## Plan First

Review the repository and propose a step-by-step implementation and verification plan. Do not edit application files, update dependencies, create environments, or execute application stages until I explicitly approve the plan.

Keep changes simple and appropriate for this Python 2 course, which uses Python 3. This is the final task for Nicolas Cava's data preparation refactor, not authorization to rewrite teammates' components.

## Goal and References

Verify that the merged Task 1-4 changes work together and preserve the complete analytical workflow and automated PDF report. Bring documentation and dependency declarations into agreement with what is actually verified.

Review:

- `data_preparation/`: loading, validation, database, analytical functions, and `DataCleaner`.
- Scripts in `01_Data_Collection/`, `02_Database/`, and `03_Data_Cleaning/`.
- `Application/main.py`: seven-stage entry point and failure handling.
- `04_EDA/` and `05-Report/`: downstream interfaces and expected outputs.
- All tests under `tests/`, `environment.yml`, and `README.md`.
- Submission 2 task prompts and `nicos_devlog.md`.

## Requirements After Plan Approval

### 1. Confirm Merged Integration

- Check the current branch and working tree; preserve pre-existing changes.
- Confirm all Task 1-4 modules, public exports, launchers, and tests are present. Task 3 files were temporarily absent during Task 4; verify their restored state and rerun their tests.
- Review package imports and ensure importing modules or launchers does not run stages or generate outputs.
- Confirm required data columns and output paths agree between preparation, cleaning, EDA, and reporting.
- Fix only concrete integration defects within Nicolas's scope. Identify broader teammate-owned issues clearly; propose any necessary changes in the plan before implementing them.
- Preserve data rules, exact ID matching, row structure, nullable types, analytical calculations, chart design, and report content.

### 2. Run Tests and the Complete Entry Point Safely

- Run the existing test suite in `cop3045`, including analytical and cleaning tests together. Report actual test counts and failures rather than relying on earlier counts.
- Add focused integration tests only for meaningful gaps discovered during review; avoid tests that merely repeat implementation details.
- Create an isolated temporary project copy containing the required code and raw data, excluding Git metadata and unnecessary generated artifacts.
- Run the copied `Application/main.py` with the selected project interpreter from a different working directory. Do not regenerate outputs in the original repository.
- Confirm all seven stages finish successfully with a zero exit status and generate fresh collection CSVs, five database source tables, the analytical CSV, cleaned CSV, EDA outputs, four report charts, and a nonempty PDF.
- Validate data preparation invariants: source jobs retained, one row per job in analytical and cleaned outputs, expected columns, and unchanged current-data results compared with verified baselines where available. Do not hard-code dataset counts in production code.
- Confirm PDF page count and expected report sections using available PDF tooling. If rendering or visual inspection is needed, follow the PDF skill and keep inspection artifacts outside the repository. Report the actual level of PDF validation performed.
- Verify that expected failures stop the workflow with a nonzero status and do not report successful completion. Prefer focused mocks or isolated fixtures rather than rerunning the full pipeline for every error case.
- Record the exact interpreter, test commands, integration command, and results.

### 3. Review the Conda Environment

- Inspect runtime imports and installed direct package versions without exposing unrelated environment details or secrets.
- Compare them with the current `environment.yml`; do not assume existing pins are correct merely because tests pass in an already populated environment.
- Ensure dependencies needed for collection, SQLite/SQLAlchemy, cleaning, EDA, plotting, and PDF reporting are declared. Keep standard-library modules out of dependency declarations.
- Preserve the existing working PDF implementation: legacy `fpdf` and `fpdf2` share an import name and must not be installed together. Do not migrate PDF libraries in this task.
- Update `environment.yml` only where evidence supports a correction. Do not blindly export the entire machine environment or add machine-specific paths.
- Verify a separate environment from the file when practical, without altering the user's existing `cop3045` environment. Include the proposed environment name and creation approach in the plan.
- Use offline/local package information first. If remote package availability or current package documentation must be checked, use authoritative sources and report any network limitation.
- A passing run in `cop3045` alone does not prove clean-environment reproducibility. Distinguish a successful clean creation/test from a solver check or an incomplete attempt; document unresolved limitations honestly.

### 4. Update Documentation

- Update `README.md` to describe the final data preparation package, its reusable functions, and the `DataCleaner` class.
- Explain constructor attributes, instance methods, and underscore-based encapsulation briefly in beginner-friendly language.
- Document the existing entry point, standalone preparation commands, test commands, generated output locations, and the fact that running stages replaces their outputs.
- Explain setup using the actual environment file and the verified PDF library.
- Preserve the skills coverage limitation and existing data-source attribution limitations.
- Correct stale structure, dependency, test-count, or verification statements based on evidence. Distinguish historical validation from current results.
- Do not rewrite historical task prompts or devlog entries to erase earlier limitations.
- Keep team ownership clear and avoid claiming Nicolas implemented teammates' EDA or reporting work.

### 5. Git Workflow and Completion

- Recommend a feature branch and meaningful commit message; do not create commits, push, merge, or open pull requests without my instruction.
- Review the final diff for scope, whitespace errors, accidental outputs, and unintended dependency changes.
- Summarize files changed, test and integration results, dependency verification, and remaining limitations.
- Do not claim the entire team submission satisfies every rubric item merely because Nicolas's work passes verification; team contribution balance and GitHub history require separate evidence.
- Append a short dated entry to `nicos_devlog.md` summarizing completed work and validation results. Preserve existing entries.

## Expected Scope

Likely changes are `README.md`, evidence-supported corrections to `environment.yml`, a small integration test file if justified, and `nicos_devlog.md`. Small preparation or entry-point fixes are allowed only as identified in the approved plan, with targeted validation.

Do not change raw data, analytical or cleaning policies, EDA behavior, chart design, PDF layout, or existing generated outputs in the original repository. Use temporary project copies for integration runs. No new application feature or abstraction is required.
