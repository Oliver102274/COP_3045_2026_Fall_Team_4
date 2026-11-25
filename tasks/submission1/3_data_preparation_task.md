# Clean and Prepare Data

Clean and prepare '02_Database/consolidated_data_database.csv' for analysis

## Output

After I approve the plan:

1. Create the folder '03_Data_Cleaning'
2. Create '03_Data_Cleaning/clean_data.py'
3. Do not execute the Python file. I will run it manually

## Python Script

Organize the script into four steps:

### 1. Read Data

Read '02_Database/consolidated_data_database.csv' into a pandas DataFrame named 'df'.

### 2. Inspect Data

Inspect the DataFrame to identify:

* Missing values
* Duplicate rows
* Data types

### 3. Clean and Prepare Data

* Remove exact duplicate rows. Verify `job_id` is non-null and unique; report and stop on missing IDs or conflicting duplicate IDs.
* Keep jobs with missing values, including skills and country trends. Do not fill missing salaries or experience with zero or averages.
* Convert salary, experience, and year columns to numeric types; report unconvertible values and set them to missing.
* Set negative salaries to missing. If `salary_min_usd` exceeds `salary_max_usd`, report the invalid range and set both bounds to missing.
* Set negative `min_experience_years` to missing; retain zero as valid.
* Trim whitespace and standardize equivalent labels in `job_title`, `country`, `experience_level`, and `remote_type`. Keep Remote, Hybrid, and Onsite distinct.
* Validate `posted_year` as a whole-number year from 2020 through 2026; set invalid years to missing and retain all valid years.
* Print before-and-after row counts, duplicates removed, missing-value counts, and invalid values found or changed.
* Leave derived calculations, summaries, charts, and current-year filtering for EDA.
* Keep the implementation simple.

### 4. Save Clean Data

Save the cleaned DataFrame as:

'03_Data_Cleaning/clean_data.csv'

Do not include the DataFrame index.

Keep the code simple and clearly identify the four steps with comments.
