import os
import io
import requests
import pandas as pd
from datetime import datetime, timezone


OWID_URL = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
RAW_OUTPUT = os.path.join("data", "owid-covid-data.csv")
PROCESSED_OUTPUT = os.path.join("data", "covid_processed.parquet")


def ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


def download_owid_csv() -> pd.DataFrame:
    print(f"Downloading OWID dataset from {OWID_URL} ...")
    response = requests.get(OWID_URL, timeout=60)
    response.raise_for_status()
    # Save raw CSV for reference
    ensure_data_dir()
    with open(RAW_OUTPUT, "wb") as f:
        f.write(response.content)
    print(f"Saved raw CSV to {RAW_OUTPUT}")
    return pd.read_csv(io.BytesIO(response.content))


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Keep relevant columns; many more exist if you need them later
    wanted = [
        "iso_code",
        "continent",
        "location",
        "date",
        "population",
        "total_cases",
        "new_cases",
        "total_deaths",
        "new_deaths",
        "total_tests",
        "new_tests",
        "total_vaccinations",
        "people_vaccinated",
        "people_fully_vaccinated",
        "new_vaccinations",
        "stringency_index",
    ]
    df = df[wanted].copy()

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Add helpful per-100k metrics where population is known
    with pd.option_context("mode.use_inf_as_na", True):
        pop = df["population"].replace({0: pd.NA})
        scale = 100_000
        df["total_cases_per_100k"] = (df["total_cases"] / pop) * scale
        df["total_deaths_per_100k"] = (df["total_deaths"] / pop) * scale
        df["new_cases_per_100k"] = (df["new_cases"] / pop) * scale
        df["new_deaths_per_100k"] = (df["new_deaths"] / pop) * scale

    # Drop rows with invalid iso codes like aggregates starting with 'OWID_'
    df = df[~df["iso_code"].fillna("").str.startswith("OWID_")]

    return df


def save_processed(df: pd.DataFrame) -> None:
    ensure_data_dir()
    # Use parquet for faster loading in the app
    df.to_parquet(PROCESSED_OUTPUT, index=False)
    print(f"Saved processed dataset to {PROCESSED_OUTPUT}")


def main() -> None:
    ensure_data_dir()
    df = download_owid_csv()
    df = process_dataframe(df)
    save_processed(df)
    print("Done.")


if __name__ == "__main__":
    main()


