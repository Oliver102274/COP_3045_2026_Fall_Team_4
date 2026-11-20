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
│
├── 00_Raw_Data/                 # Original datasets and data dictionaries
├── 01_Data_Collection/          # Data collection and consolidation
├── 02_Database/                 # Database and analytical dataset
├── 03_Data_Cleaning/            # Data cleaning and preparation
├── 04_EDA/                      # Exploratory data analysis
├── 05-Report/                   # PDF reports and visualizations
│   ├── generate_report.py       # Standalone reporting launcher
│   └── reporting/              # Reusable reporting package
│       ├── __init__.py          # Exposes ReportGenerator
│       ├── analysis.py          # Loading, validation, statistics, findings
│       ├── charts.py            # Four reusable chart functions
│       └── report.py            # ReportGenerator class and PDF layout
├── Application/                # Application entry point
│   └── main.py                  # Runs all seven workflow stages
├── tests/
│   └── test_reporting.py        # Reporting regression and validation tests
│
├── README.md                    # Project documentation
├── environment.yml              # Conda environment configuration
├── 1_database_task.md            # Project task documentation
├── 2_analytical_dataset_task.md  # Project task documentation
├── 3_data_preparation_task.md    # Project task documentation
└── 6-automated_report_task.md    # Project task documentation
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

`environment.yml` pins the tested Python version, **3.14.7**, and direct package versions. It uses the `defaults` and `conda-forge` channels and pip for the packages installed from PyPI in the verified environment. **Legacy `fpdf==1.7.2` is the only declared PDF implementation**; do not also install `fpdf2`, which shares the `fpdf` import name. The existing report has not been verified with fpdf2.

If you already have a `cop3045` environment, create a separate environment instead of updating it in place:

```bash
conda env create -f environment.yml -n cop3045-submission2
conda activate cop3045-submission2
```

The current working environment passes all 17 reporting tests and the seven-stage integration check. A separate offline Conda creation resolved and installed the Conda packages, but Windows activation failed with exit code `9020` before pip dependencies could be installed. Clean-environment verification therefore remains incomplete. Create the separate environment above on a working Conda installation and rerun the tests and full workflow before claiming complete reproducibility. Exact direct-version pins are not a lockfile for every transitive dependency.

### 📝 Generate Only the PDF

After activating the environment, run from the repository root:

```bash
python 05-Report/generate_report.py
```

This requires an existing `03_Data_Cleaning/clean_data.csv`. Run the full application first if the cleaned file is missing or needs to be regenerated. Reporting writes the same PDF and four PNGs without rerunning collection, database creation, cleaning, or EDA. To launch from another directory, use the full path to either entry-point script; data paths are resolved from the script location.

### ✅ Run the Reporting Tests

From the repository root with the environment activated:

```bash
python -B -m unittest discover -s tests -v
```

The 17 tests cover baseline statistics, tied findings, missing values, invalid input, chart/PDF output failures, and imports without output generation. Output-failure tests use temporary directories. The baseline-data test reads the included cleaned CSV; the tests do not run the full application or overwrite project outputs.

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
