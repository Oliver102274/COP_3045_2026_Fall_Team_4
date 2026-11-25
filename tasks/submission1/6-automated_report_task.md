# Automated PDF Report

Create an automated PDF report using `fpdf2`.

Use:

`03-Data cleaning/clean_data.csv`

The report should automatically analyze the cleaned AI job market dataset and summarize important patterns related to job roles, salaries, experience levels, work arrangements, and job postings over time.

## Output

After I approve the plan:

1. Create the folder `05-Report`.
2. Create `05-Report/generate_report.py`.
3. Do not modify files created in previous tasks.
4. Do not execute the Python file. I will run it manually.

When `generate_report.py` is executed, it should automatically create:

`05-Report/project_report.pdf`

The visualizations used in the report should also be saved in the `05-Report` folder.

## Python Script

The Python script must be self-contained. It should read the cleaned dataset and generate all content needed for the PDF report.

Keep the implementation very basic. The script should run sequentially from top to bottom using simple Python syntax.

Do not use:

- Functions (`def`)
- Classes (`class`)
- Helper functions
- A custom `FPDF` class
- `if __name__ == "__main__"`
- `pathlib`
- `tempfile`
- Context managers
- Advanced abstractions or complicated fallback logic

Use:

- Simple imports
- Simple string paths
- Variables
- Basic `if` statements and `for` loops when needed
- Direct pandas commands
- Direct Matplotlib and Seaborn commands
- Direct `FPDF` commands

Prioritize simplicity over robustness, reusability, or flexibility.

## Report Goal

Create an automated report that provides a simple overview of the AI job market represented in the cleaned dataset.

The report should focus on:

- Common AI/data job roles
- Salary information
- Experience levels
- Remote, hybrid, and onsite work arrangements
- Job posting patterns over time

All statistics, chart values, and analytical findings must be calculated automatically from `clean_data.csv`. Do not hard-code analytical results into the PDF.

### 1. Project Title

Use a clear title such as:

**AI Job Market Analysis: Roles, Salaries, Experience, and Work Arrangements**

### 2. Dataset Summary

Automatically generate a brief summary of the dataset, including:

- Number of observations
- Number of variables
- Years represented in the dataset
- Number of countries represented
- Number of standardized job titles
- Number of experience levels
- Number of work arrangement categories

Keep the summary simple and calculate the values directly from the dataset.

### 3. Summary Statistics

Automatically calculate relevant summary statistics for these important job-level numerical variables:

- `min_experience_years`
- `salary_min_usd`
- `salary_max_usd`

Include simple statistics such as:

- Mean
- Minimum
- Median
- Maximum

Present the results using a simple table in the PDF.

Keep the table small and easy to read.

### 4. Visualizations

Create and save four informative visualizations using simple Matplotlib and Seaborn commands.

#### Visualization 1: Job Postings by Standardized Job Title

Create a bar chart showing the number of job postings for each `standardized_title`.

Purpose: Show which AI/data roles appear most frequently in the dataset.

#### Visualization 2: Salary by Experience Level

Create a box plot comparing `salary_max_usd` across `experience_level`.

Purpose: Show how salary distributions differ between experience levels.

#### Visualization 3: Work Arrangement Distribution

Create a bar chart or count plot showing the number of jobs for each `remote_type`.

Purpose: Compare Remote, Hybrid, and Onsite job opportunities.

#### Visualization 4: Job Postings by Year

Group the data by `posted_year`, count the number of job postings for each year, and create a line chart.

Purpose: Show how the number of job postings represented in the dataset changes across the available years.

Each visualization should have:

- A clear title
- Appropriate x-axis and y-axis labels
- Readable formatting

Save each visualization as an image file inside `05-Report` and include it in the PDF report.

Keep all plotting code simple.

### 5. Key Analytical Findings

Automatically calculate a few simple descriptive findings from the dataset.

Include findings such as:

- The standardized job title with the highest number of postings
- The experience level with the highest average salary
- The most common work arrangement (`remote_type`)
- The year with the highest number of job postings

Calculate these findings directly from the dataset using simple pandas operations.

Convert the calculated results into short sentences and automatically add those sentences to the PDF.

Do not hard-code the answers. The findings must update automatically if the cleaned dataset changes.

### 6. Skills Data

Do not use the `skills` column as a primary analysis or visualization because most observations in the current cleaned dataset do not contain a value for this column.

The report may mention the amount of available skills data if useful, but skills should not be presented as a complete representation of the full dataset.

## PDF Generation

Use `fpdf2` to generate the complete PDF report.

Create the PDF directly with:

`pdf = FPDF()`

Use basic `FPDF` commands to add:

- Pages
- Project title
- Section headings
- Dataset summary
- Paragraphs
- Summary-statistics table
- Visualization images
- Key analytical findings

Keep the PDF layout simple, organized, and readable.

The complete report must be generated automatically by executing `generate_report.py`.

Save the final PDF as:

`05-Report/project_report.pdf`

Do not modify or depend on Python files created in previous tasks.
