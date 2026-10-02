from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Build paths relative to this script so the terminal's location does not matter.
DATABASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = DATABASE_DIR.parent / "00_Raw_Data"


if __name__ == "__main__":
    # Step 1: Instantiate Database.
    # SQLite creates project.db when the connection opens, if it does not exist.
    database_url = URL.create("sqlite", database=str(DATABASE_DIR / "project.db"))
    engine = create_engine(database_url)
    connection = engine.connect()

    try:
        # Step 2: Read Data.
        # Load each of the five source CSV files into its own pandas DataFrame.
        ai_jobs_df = pd.read_csv(RAW_DATA_DIR / "ai_jobs.csv")
        country_ai_trends_df = pd.read_csv(RAW_DATA_DIR / "country_ai_trends.csv")
        data_dictionary_df = pd.read_csv(RAW_DATA_DIR / "data_dictionary.csv")
        job_title_mapping_df = pd.read_csv(RAW_DATA_DIR / "job_title_mapping.csv")
        skills_demand_df = pd.read_csv(RAW_DATA_DIR / "skills_demand.csv")

        # Step 3: Create Tables.
        # Each dictionary key becomes a table name in the SQLite database.
        datasets = {
            "ai_jobs": ai_jobs_df,
            "country_ai_trends": country_ai_trends_df,
            "data_dictionary": data_dictionary_df,
            "job_title_mapping": job_title_mapping_df,
            "skills_demand": skills_demand_df,
        }

        # Commit the inserts when the transaction completes successfully.
        with connection.begin():
            for table_name, dataframe in datasets.items():
                # replace recreates an existing table; index=False prevents
                # pandas' row index from becoming an extra database column.
                dataframe.to_sql(
                    name=table_name,
                    con=connection,
                    if_exists="replace",
                    index=False,
                )

    finally:
        # Step 4: Close Connection.
        # Release database resources even if reading or writing raises an error.
        connection.close()
        engine.dispose()
