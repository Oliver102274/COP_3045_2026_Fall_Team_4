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
<<<<<<< HEAD
├── 00_Raw_Data/                 # Original datasets and data dictionaries
├── 01_Data_Collection/          # Data collection and consolidation
├── 02_Database/                 # Database and analytical dataset
├── 03_Data_Cleaning/            # Data cleaning and preparation
├── 04_EDA/                      # Exploratory data analysis
├── 05-Report/                   # Reports and visualizations
├── Application/                # Application entry point
│   └── main.py                  # Runs all seven workflow stages
│
├── README.md                    # Project documentation
├── environment.yml              # Conda environment configuration
├── 1_database_task.md            # Project task documentation
├── 2_analytical_dataset_task.md  # Project task documentation
├── 3_data_preparation_task.md    # Project task documentation
└── 6-automated_report_task.md    # Project task documentation
```
=======
├── 00_Raw_Data/          # Original datasets and data dictionaries
├── 01_Data_Collection/   # Data collection and consolidation
├── 02_Database/          # Database and analytical dataset
├── 03_Data_Cleaning/     # Data cleaning and preparation
├── 04_EDA/               # Exploratory data analysis
├── 05-Report/            # PDF reports and visualizations
├── Application/          # Main application entry point
│   └── main.py           # Runs the complete workflow
│
├── README.md             # Project documentation
├── environment.yml       # Conda environment configuration
└── *.md                  # Project task documentation    
>>>>>>> 5da6c512d99dbdbc2842cfd6d8f821181839d0f4

📈 Visualizations & Reporting

The automated reporting component includes visualizations such as:

* 📅 Job postings by year
* 💰 Salary by experience level
* 🏷️ Standardized job title distributions
* 🏠 Work arrangement distributions

The repository also includes a generated PDF report that presents the reporting component’s outputs.

🚀 Getting Started

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
