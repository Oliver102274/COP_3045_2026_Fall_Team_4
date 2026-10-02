# Create SQLite Database

Create a SQLite database using **pandas and SQLAlchemy**

## Source Files

Use these files from '00_Raw_Data':

* 'ai_jobs.csv'
* 'country_ai_trends.csv'
* 'data_dictionary.csv'
* 'job_title_mapping.csv'
* 'skills_demand.csv'

## Output

After I approve the plan:

1. Create the folder '02_Database'
2. Create '02_Database/instantiate_database.py'
3. Do not execute the Python file. I will run it manually.

While executed, 'instantiate_database.py' should create '02_Database/project.db'.

Do not include code in 'instantiate_database.py' to create the '02_Database' folder. You should create the folder before creating the Python file.

## Python Script

Organize 'instantiate_database.py' into four steps:

### 1. Instantiate Database

* Create a SQLite engine using SQLAlchemy
* Connect to 'project.db'

### 2. Read Data

Read the five CSV files into pandas Dataframes.

### 3. Create Tables

Create these tables using 'Dataframe.to_sql()'

* 'ai_jobs'
* 'country_ai_trends'
* 'data_dictionary'
* 'job_title_mapping'
* 'skills_demand'

Use:

* 'if_exists="replace"'
* 'index=False'

### 4. Close Connection

Close the database connection.

Keep the code simple and clearly identify the four steps with comments