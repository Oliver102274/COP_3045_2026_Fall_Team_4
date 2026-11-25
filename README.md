# COP_3045_2026_Fall_Team_4
✨ AI & Data Science Job Market Analysis 🤖

Turning job market data into insights about the future of AI and data science careers. 📊💼

⸻

🌷 About the Project

The AI & Data Science Job Market Analysis is a collaborative project developed by a team of four students at Florida International University (FIU) for COP 3045.

The project explores the AI and data science job market through data collection, database development, data cleaning, exploratory data analysis, visualization, and automated reporting.

By transforming raw datasets into structured analytical outputs, the project demonstrates how Python and data science tools can help organize information and explore employment trends.

🎯 Project Objectives

* 📥 Collect and consolidate job market datasets.
* 🧹 Clean and prepare data for analysis.
* 🗄️ Build a database and analytical dataset.
* 🔎 Perform exploratory data analysis (EDA).
* 📊 Visualize patterns and distributions in the data.
* 📝 Generate an automated PDF report.

⚙️ Project Workflow

1. 📂 Raw Data
2. 📥 Data Collection & Consolidation
3. 🗄️ Database & Analytical Dataset
4. 🧹 Data Cleaning & Preparation
5. 🔎 Exploratory Data Analysis
6. 📈 Visualizations & Automated Reporting
7. ✨ Final Project Report

📊 What We Explore

Our project includes datasets and analyses related to:

* 💼 AI and data science job postings
* 🌎 Country-level AI job market trends
* 🛠️ In-demand technical skills
* 📅 Job postings across different years
* 💰 Salary differences by experience level
* 🏠 Remote, hybrid, and on-site work arrangements
* 🏷️ Standardized job titles and job categories

Findings and conclusions depend on the available datasets and the analyses performed by the team.

### 📚 Dataset Sources

The application reads the five CSV files included in `00_Raw_Data/`; no download or API key is needed to run it:

| File | Role |
|---|---|
| `ai_jobs.csv` | Individual job postings, salary bounds, and experience requirements |
| `country_ai_trends.csv` | Country/year job-market statistics |
| `job_title_mapping.csv` | Original job titles mapped to standardized titles and role categories |
| `skills_demand.csv` | Skill records linked to jobs by exact job ID |
| `data_dictionary.csv` | Source column descriptions |

The original publisher, download URL, and dataset license are not recorded in this repository. The team must confirm and add that attribution before submission; these files should not be described as independently collected or representative of the entire job market.

🛠️Tech Stack

### 💻 Languages & Libraries

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0?style=for-the-badge)

### 🗄️ Database & Reporting

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge)
![FPDF](https://img.shields.io/badge/FPDF-PDF%20Reports-E44D26?style=for-the-badge)

### 🤝 Development & Collaboration

![Conda](https://img.shields.io/badge/Conda-44A833?style=for-the-badge&logo=anaconda&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

---

**✨ How We Used These Technologies**

- 🐍 **Python:** Main programming language for the data science workflow.
- 🧹 **Pandas & NumPy:** Data processing, cleaning, and analysis.
- 📊 **Matplotlib & Seaborn:** Data visualization and exploratory analysis.
- 🗄️ **SQLite & SQLAlchemy:** Database storage and management.
- 📝 **FPDF:** Automated PDF report generation.
- 🌱 **Conda:** Python environment and dependency management.
- 🔄 **Git & GitHub:** Version control and team collaboration.

*Built collaboratively by a team of four FIU students. 💗*

Key concepts in practice:

* CSV data handling and consolidation across related datasets
* Data cleaning and transformation before analysis
* Connecting individual scripts into a reproducible workflow

📁 Repository Structure

```text
COP_3045_2026_Fall_Team_4/
|-- 00_Raw_Data/                          # Original source datasets
|   |-- ai_jobs.csv                       # Job postings and salary information
|   |-- country_ai_trends.csv             # Country/year job-market statistics
|   |-- data_dictionary.csv               # Source column descriptions
|   |-- job_title_mapping.csv             # Standardized titles and role categories
|   `-- skills_demand.csv                 # Skills linked to job IDs
|-- 01_Data_Collection/
|   |-- data_collection.py                # Load and consolidate job/skill records
|   `-- output/                           # Consolidated and unmatched-skills CSVs
|-- 02_Database/
|   |-- instantiate_database.py           # Create the five SQLite source tables
|   |-- create_analytical_dataset.py       # Build and export one row per job
|   |-- project.db                        # Generated SQLite database
|   `-- consolidated_data_database.csv    # Generated analytical dataset
|-- 03_Data_Cleaning/
|   |-- clean_data.py                     # Run the cleaning workflow
|   `-- clean_data.csv                    # Prepared dataset for EDA and reporting
|-- 04_EDA/
|   |-- nongraphical_analysis.py           # Calculate descriptive analysis tables
|   |-- eda_analysis.py                   # Generate exploratory charts
|   `-- output/                           # Generated analysis tables and charts
|-- 05-Report/
|   |-- generate_report.py                # Run automated PDF reporting
|   |-- reporting/
|   |   |-- __init__.py                   # Expose ReportGenerator
|   |   |-- analysis.py                   # Validate data and calculate report findings
|   |   |-- charts.py                     # Reusable EDA and report chart functions
|   |   `-- report.py                     # ReportGenerator class and PDF layout
|   |-- project_report.pdf                # Generated PDF report
|   `-- *.png                             # Four generated report charts
|-- Application/
|   `-- main.py                           # Coordinate all seven workflow stages
|-- data_preparation/                     # Reusable data preparation package
|   |-- __init__.py                       # Expose public functions and DataCleaner
|   |-- loading.py                        # Discover and read source CSV files
|   |-- validation.py                     # Check required sources, columns, and keys
|   |-- database.py                       # Create databases and read source tables
|   |-- analytical.py                     # Join datasets and calculate skills coverage
|   `-- cleaning.py                       # DataCleaner class and cleaning operations
|-- tasks/                                # Project task prompts
|   |-- submission1/
|   |   |-- 1_database_task.md             # Original database creation task
|   |   |-- 2_analytical_dataset_task.md   # Original analytical dataset task
|   |   |-- 3_data_preparation_task.md     # Original cleaning task
|   |   `-- 6-automated_report_task.md     # Original PDF reporting task
|   `-- submission2/
|       |-- submission2_01_data_loading_task.md            # Loading refactor task
|       |-- submission2_02_database_task.md                # Database refactor task
|       |-- submission2_03_analytical_dataset_task.md      # Analytical refactor task
|       |-- submission2_04_data_cleaning_task.md           # Cleaning class task
|       `-- submission2_05_integration_validation_task.md # Integration and documentation task
|-- tests/
|   |-- test_data_loading.py              # CSV loading and source validation tests
|   |-- test_database.py                  # Database creation and reading tests
|   |-- test_analytical_dataset.py         # Analytical joins and skills coverage tests
|   |-- test_data_cleaning.py              # Cleaning rules and DataCleaner tests
|   |-- test_application.py                # Entry-point failure-handling tests
|   `-- test_reporting.py                 # Report analysis and generation tests
|-- .gitignore                            # Files excluded from version control
|-- environment.yml                       # Conda environment and dependencies
`-- README.md                             # Setup, architecture, and usage guide
```

📈 Visualizations & Reporting

The automated reporting component includes visualizations such as:

* 📅 Job postings by year
* 💰 Salary by experience level
* 🏷️ Standardized job title distributions
* 🏠 Work arrangement distributions

Running the application generates `05-Report/project_report.pdf`: six pages covering the dataset summary and statistics, four visualizations, and key findings and limitations. The four report charts are saved alongside it:

- `standardized_title_postings.png`
- `salary_by_experience_level.png`
- `work_arrangement_distribution.png`
- `job_postings_by_year.png`

Earlier stages write consolidated CSVs under `01_Data_Collection/output/`, the database and analytical CSV under `02_Database/`, `03_Data_Cleaning/clean_data.csv`, and EDA tables and charts under `04_EDA/output/`. Running the full application regenerates these outputs, including the database.

### 🧩 Reporting Architecture

`generate_report.py` provides a small `main()` function and execution guard. It creates a `ReportGenerator` and calls `generate()`; importing the package does not generate files.

- `analysis.py` loads and validates the cleaned CSV and calculates statistics and findings without cleaning or replacing data.
- `charts.py` provides four reusable plotting functions with the original chart design.
- `report.py` defines `ReportGenerator`: its constructor stores `_data_file` and `_output_dir`, `generate()` coordinates reporting, and `_write_pdf()` preserves the original PDF layout. Underscores mark internal implementation details by convention.
- Functions and methods have type hints and docstrings. Missing or unusable input and output failures produce descriptive errors, and a failed reporting stage stops the application.

The report preserves the first submission's calculations and analytical limitations. It does not treat missing skills as proof that a job requires no skills.

### Data Preparation Architecture

Nicolas's `data_preparation` package supplies reusable CSV loading, source validation, database creation, read-only table loading, analytical joins, and cleaning. The original stage scripts coordinate these operations; importing them does not run the workflow. Paths come from script locations, allowing direct execution from another working directory. The intentional imports after path setup use `# noqa: E402` where applicable.

Collection retains one row per job/skill match. The analytical dataset aggregates sorted unique skill names and retains one row per original job, including jobs without skills or lookup matches. Exact IDs are used without guessed corrections. Incomplete skills matches limit skills analysis; missing skills do not mean no skills are required.

`DataCleaner(input_path, output_path)` stores `_input_path` and `_output_path` without reading files. Its `run()` method loads, cleans, reports, and saves data; `clean_dataframe(df)` cleans a copy without file access and expects pandas string columns, matching `read_csv(dtype="string")`. Internal helper methods separate duplicate/ID checks, text normalization, numeric conversion, invalid-value rules, and summaries. Underscores mark internal attributes and methods by convention, demonstrating encapsulation.

Cleaning preserves missing values and exact nonblank IDs, rejects conflicting IDs, masks invalid salary/experience values, and retains whole-number posting years from 2020 through 2026. It does not calculate EDA measures or filter to the current year.

### Run Preparation Stages Individually

From the repository root with `cop3045` activated:

```bash
python 01_Data_Collection/data_collection.py
python 02_Database/instantiate_database.py
python 02_Database/create_analytical_dataset.py
python 03_Data_Cleaning/clean_data.py
```

Database creation reads the raw CSVs directly; analytical creation needs the database, and cleaning needs the analytical CSV. Running these commands replaces the corresponding generated outputs. Use a separate project copy to preserve existing outputs.

🚀 Getting Started

Install Miniconda or Anaconda first, then open a Conda-enabled terminal (for example, Anaconda Prompt on Windows). Git is needed for the clone command; alternatively, download and extract the repository ZIP and open a terminal in its project folder.

1. Clone the repository

   ```bash
   git clone https://github.com/Oliver102274/COP_3045_2026_Fall_Team_4.git
   ```

2. Navigate to the project folder

   ```bash
   cd COP_3045_2026_Fall_Team_4
   ```

3. Create and activate the Conda environment (with Conda installed)

   ```bash
   conda env create -f environment.yml
   conda activate cop3045
   ```

4. Run the application

   From the repository root, run the complete workflow:

   ```bash
   python Application/main.py
   ```

   The final PDF is saved to `05-Report/project_report.pdf`.

### 🌱 Environment Notes

`environment.yml` pins the tested Python version, **3.14.7**, and direct package versions. Task 5 aligned the optional notebook dependency `ipykernel` with the installed version, **7.2.0**; all other declared direct versions matched the tested environment. It uses the `defaults` and `conda-forge` channels and pip for the packages installed from PyPI in the verified environment. **Legacy `fpdf==1.7.2` is the only declared PDF implementation**; do not also install `fpdf2`, which shares the `fpdf` import name. The existing report has not been verified with fpdf2.

If you already have a `cop3045` environment, create a separate environment instead of updating it in place:

```bash
conda env create -f environment.yml -n cop3045-submission2
conda activate cop3045-submission2
```

Validation on November 24, 2026 used `C:/Users/nmcav/anaconda3/envs/cop3045/python.exe` (Python 3.14.7). The complete merged suite and isolated seven-stage workflow were verified in that existing environment. A new offline environment was attempted at a temporary prefix using `conda env create --prefix "<temporary-folder>/cop3045-submission2-validation-20261124" --file environment.yml --offline --yes`. Creation failed during dependency resolution because cached channel metadata/packages were unavailable; this does not establish whether those packages are available online. No successful clean-environment creation or test is claimed. Use the separate environment commands above on a connected Conda installation, then rerun tests and the workflow. Exact direct-version pins are not a transitive lockfile.

### 📝 Generate Only the PDF

After activating the environment, run from the repository root:

```bash
python 05-Report/generate_report.py
```

This requires an existing `03_Data_Cleaning/clean_data.csv`. Run the full application first if the cleaned file is missing or needs to be regenerated. Reporting writes the same PDF and four PNGs without rerunning collection, database creation, cleaning, or EDA. To launch from another directory, use the full path to either entry-point script; data paths are resolved from the script location.

### ✅ Run All Tests

From the repository root with the environment activated:

```bash
python -B -m unittest discover -s tests -v
```

The 64 tests cover loading, source validation, database operations, analytical joins and skills coverage, cleaning, entry-point failure handling, and reporting. Tests use temporary outputs or mocks; the reporting baseline test reads the included cleaned CSV. They do not run the full application or overwrite project outputs. All 64 passed in the existing `cop3045` environment on November 24, 2026.

To run one preparation component, substitute its filename:

```bash
python -B -m unittest discover -s tests -p "test_data_cleaning.py" -v
```

### Integration Verification

The merged Tasks 1-4 were present and tested together. The verification ran the copied entry point as `"C:/Users/nmcav/anaconda3/envs/cop3045/python.exe" -B "<temporary-project>/Application/main.py"` from outside that copied project. It exited with status 0 after all seven stages. Starting without generated outputs produced five SQLite source tables, collection CSVs, 50,000-row/21-column analytical and cleaned CSVs, EDA tables, three EDA charts, four report charts, and a nonempty PDF. Both job-level CSVs matched the included baseline DataFrames, retained all original job IDs exactly once, and all original CSV/database/chart/PDF hashes remained unchanged.

The PDF received a structural content-stream check: six page objects and the expected summary, statistics, four chart headings, findings, and limitations. All seven PNGs decoded successfully. No PDF renderer or parser was installed, so page layout was not visually inspected; open the generated report locally to check layout before submission. Poppler (`pdfinfo` and `pdftoppm`) can provide independent page-count and rendering checks. A Seaborn/Matplotlib deprecation warning was observed without test failure; no plotting behavior was changed.

Entry-point tests additionally confirm that a failed stage prevents later stages and successful-completion messages, and that a missing final PDF returns failure. Clean-environment reproducibility remains incomplete as described above.

For the full integration check, run `python Application/main.py` and confirm all seven stages finish and the six-page PDF plus four report charts are produced. Use a separate project copy if you need to preserve existing generated files.

👥 Team Collaboration

This project was developed collaboratively by four students as part of a university programming course.

The project brings together multiple stages of the data science workflow, from collecting and preparing datasets to analyzing results and generating a report.

Each component contributes to the overall pipeline, demonstrating how separate tasks can be integrated into a complete data analysis project.

* **Nicolas Cava** — Data cleaning and preparation.
* **Ruben Barndzhian** — Non-graphical exploratory data analysis.
* **Dawid Hunicz** — Graphical exploratory data analysis.
* **Oliver Hernández** — Automated PDF reporting and application integration.

🎓 Academic Information

* Institution: Florida International University (FIU)
* Course: COP 3045 — Fall 2026
* Project: AI & Data Science Job Market Analysis
* Team size: 4 students

⸻

💗 Data tells a story. Good analysis helps us understand it. ✨

Built collaboratively with Python, teamwork, and a little bit of data magic. 🪄
