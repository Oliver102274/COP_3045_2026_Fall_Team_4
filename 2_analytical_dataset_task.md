# Create Analytical Dataset

Create a pandas DataFrame for analysis using the tables in '02_Database/project.db'

* 'ai_jobs'
* 'country_ai_trends'
* 'data_dictionary'
* 'job_title_mapping'
* 'skills_demand'

## Output

After I approve the plan:

1. Create '02_Database/create_analytical_dataset.py'
2. Do not execute the Python file. I will run it manually.

## Python Script

Organize the script into four steps:

### 1. Connect to Database

* Create a SQLAlchemy engine
* Connect to '02_Database/project.db'

### 2. Read Tables

Read the tables into pandas DataFrames.

### 3. Create Analytical DataFrame

Create a single DataFrame named `df` with one row per `job_id`, using the tables read from SQLite.

Before joining, check that `ai_jobs.job_id`, `job_title_mapping.job_title`, and the combination `(country, year)` in `country_ai_trends` are non-null and unique. Raise a clear error if a check fails, as in `01_Data_Collection/data_collection.py`.

1. Left join `ai_jobs` with `job_title_mapping` using `job_title` and `validate="many_to_one"`.
2. Left join the result with `country_ai_trends` using `country` and `posted_year` (matched to `year`) and `validate="many_to_one"`. Prefix added trend columns with `country_` and avoid duplicate columns.
3. Group `skills_demand` by `job_id`, combining unique skill names into a semicolon-separated `skills` column. Left join this summary using exact `job_id` matches and `validate="one_to_one"` so jobs are not duplicated. Keep unmatched jobs and leave their skills missing; report the counts of unmatched skill rows, distinct unmatched skill IDs, and jobs without matching skills. Do not change IDs or interpret missing matches as "no skills required."
4. Keep `data_dictionary` for reference only; do not join it to job records.
5. Retain all original job columns for later analysis of salaries, experience requirements, and remote-work opportunities. Leave derived calculations, such as salary midpoint, for the EDA stage.
6. Verify that all original jobs remain and `job_id` is unique. Save `df` to `02_Database/consolidated_data_database.csv` with `index=False`.

The earlier CSV checks matched skills to only 2,050 of 50,000 jobs. Recalculate coverage from the database and document this limitation; it limits skills analysis but does not prevent salary, experience, or remote-work comparisons using the job columns.

Do not save the DataFrame as a database table or modify source tables.

### 4. Close Connection

Close the database connection

Keep the implementation simple and clearly identify the four steps with comments.
