# Step 1: Import the tools used to locate files and work with table data.
# Path builds file paths; pandas reads CSV files into tables called DataFrames.
from pathlib import Path

import pandas as pd


# Step 2: Locate the raw data folder using this Python file's location.
# __file__ is this script; resolve() gives its absolute path. The first parent
# is 01_Data_Collection, and the second is the project folder containing
# 00_Raw_Data. This works even if the terminal starts in a different folder.
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "00_Raw_Data"


def load_raw_data():
    """Load each raw CSV into a DataFrame, keyed by its filename without .csv."""
    # Step 3: Find all CSV files and load them into a dictionary.
    # glob("*.csv") selects CSV files; sorted() gives a consistent file order.
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    # Stop with a clear error if the folder is missing or contains no CSV files.
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DATA_DIR}")
    # path.stem removes the extension: ai_jobs.csv becomes the key "ai_jobs".
    # Each dictionary value is the DataFrame returned by pd.read_csv().
    return {path.stem: pd.read_csv(path) for path in csv_files}


def consolidate_data(datasets):
    """Create a job/skill table using exact keys; retain jobs without skills."""
    # Step 4: Select the four datasets that contain records we can join.
    # data_dictionary describes the source columns, so it is loaded for
    # reference but is not merged into individual job records.
    jobs = datasets["ai_jobs"]
    skills = datasets["skills_demand"]
    titles = datasets["job_title_mapping"]
    trends = datasets["country_ai_trends"]

    # Step 5: Check the keys that must uniquely identify source records.
    # Each job_id identifies one job, each job_title identifies one mapping,
    # and the combination of country AND year identifies one trend record.
    # isna() detects missing values; duplicated(keys) detects repeated keys.
    # any() makes these checks True if at least one problem exists.
    # Reject bad keys so a merge cannot silently multiply lookup matches.
    for name, frame, keys in [
        ("ai_jobs", jobs, ["job_id"]),
        ("job_title_mapping", titles, ["job_title"]),
        ("country_ai_trends", trends, ["country", "year"]),
    ]:
        if frame[keys].isna().any().any() or frame.duplicated(keys).any():
            raise ValueError(f"{name} must have non-null, unique keys: {keys}")

    # Step 6: Add standardized_title and role_category using job_title.
    # A left join keeps every job, even if no title mapping matches.
    # many_to_one allows many jobs to share one unique mapping row.
    consolidated = jobs.merge(
        titles, on="job_title", how="left", validate="many_to_one"
    )

    # Step 7: Attach country statistics for the job's country and posting year.
    # Rename year to posted_year so both tables use the same join column name.
    # Prefix the remaining statistics with country_ to show their scope:
    # country_avg_salary_usd describes the country/year, not this job's salary.
    # The ** expression adds the generated name pairs to the rename dictionary.
    trends = trends.rename(columns={
        "year": "posted_year",
        **{column: f"country_{column}" for column in trends.columns
           if column not in ["country", "year"]},
    })
    consolidated = consolidated.merge(
        trends, on=["country", "posted_year"], how="left",
        validate="many_to_one",
    )

    # Step 8: Set aside skill records whose job_id does not exist in ai_jobs.
    # isin() checks membership; ~ reverses the result to select nonmatches.
    # loc selects those rows, and copy() creates a separate DataFrame.
    # Keep exact IDs: similar-looking IDs are not proof of the same job.
    unmatched_skills = skills.loc[~skills["job_id"].isin(jobs["job_id"])].copy()

    # Step 9: Join skills to jobs using job_id (one job can have many skills).
    # A job with several skills repeats once per skill in the output.
    # Jobs without matches remain, with missing values in the skill columns.
    # skill_match is "both" for a match and "left_only" for a job without one.
    # Count unique job_id values when calculating job totals from this table.
    consolidated = consolidated.merge(
        skills, on="job_id", how="left", validate="one_to_many",
        indicator="skill_match",
    )

    # Step 10: Save the consolidated table and unmatched skills as CSV files.
    # mkdir creates the output folder; exist_ok=True allows it to exist already.
    # index=False excludes pandas' row index from the exported columns.
    # Running the script again replaces these output files with fresh results.
    output_dir = RAW_DATA_DIR.parent / "01_Data_Collection" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "consolidated_data.csv"
    consolidated.to_csv(output_path, index=False)
    unmatched_skills.to_csv(output_dir / "unmatched_skills.csv", index=False)

    # Step 11: Report the output location, row count, and unmatched records.
    # nunique() counts distinct jobs; the comma in an f-string format such as
    # {len(consolidated):,} adds thousands separators for easier reading.
    print(f"\nConsolidated file: {output_path}")
    print(f"Output rows: {len(consolidated):,}")
    print(f"Jobs without matching skills: "
          f"{consolidated.loc[consolidated['skill_match'] == 'left_only', 'job_id'].nunique():,}")
    print(f"Unmatched skill records saved separately: {len(unmatched_skills):,}")
    # Return the DataFrame so it can also be used for analysis in Python.
    return consolidated


# Step 12: Run the workflow when this file is executed directly.
# This guard prevents loading/exporting automatically if another script
# imports the functions from this file.
if __name__ == "__main__":
    datasets = load_raw_data()
    consolidated_data = consolidate_data(datasets)

    # Step 13: Keep convenient variables for inspecting each original dataset.
    # Access individual datasets by their filenames (without .csv).
    ai_jobs = datasets["ai_jobs"]
    country_ai_trends = datasets["country_ai_trends"]
    data_dictionary = datasets["data_dictionary"]
    job_title_mapping = datasets["job_title_mapping"]
    skills_demand = datasets["skills_demand"]

    # Step 14: Inspect the loaded data in the terminal.
    # items() provides each dataset name and its DataFrame.
    # shape[0] is the row count; shape[1] is the column count.
    for name, dataframe in datasets.items():
        print(f"{name}: {dataframe.shape[0]:,} rows, {dataframe.shape[1]} columns")

    # head() previews the first five rows, columns lists the column names,
    # and info() reports data types and non-null counts for each column.
    print("\nFirst five AI jobs:")
    print(ai_jobs.head())
    print(ai_jobs.columns)
    ai_jobs.info()
    print(country_ai_trends.head())
    print(country_ai_trends.columns)
    country_ai_trends.info()
    print(data_dictionary.head())
    print(data_dictionary.columns)
    data_dictionary.info()
    print(job_title_mapping.head())
    print(job_title_mapping.columns)
    job_title_mapping.info()
    print(skills_demand.head())
    print(skills_demand.columns)
    skills_demand.info()
