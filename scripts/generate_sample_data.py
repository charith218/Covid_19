import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


OUTPUT = os.path.join("data", "covid_processed.parquet")


def ensure_data_dir() -> None:
    os.makedirs("data", exist_ok=True)


def make_country_series(start: datetime, days: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    base_cases = rng.poisson(lam=500, size=days).astype(float)
    wave = 300 * np.sin(np.linspace(0, 5, days))
    noise = rng.normal(0, 50, size=days)
    new_cases = np.clip(base_cases + wave + noise, 0, None)
    new_deaths = np.clip(new_cases * rng.uniform(0.005, 0.02), 0, None)
    total_cases = np.cumsum(new_cases)
    total_deaths = np.cumsum(new_deaths)
    dates = [start + timedelta(days=i) for i in range(days)]
    return dates, new_cases, new_deaths, total_cases, total_deaths


def build_sample_dataframe() -> pd.DataFrame:
    start = datetime(2020, 3, 1)
    days = 400

    countries = [
        ("USA", "North America", "United States", 331_000_000, 1),
        ("IND", "Asia", "India", 1_380_000_000, 2),
        ("BRA", "South America", "Brazil", 212_000_000, 3),
        ("ZAF", "Africa", "South Africa", 59_000_000, 4),
        ("FRA", "Europe", "France", 65_000_000, 5),
    ]

    frames = []
    for iso, continent, name, population, seed in countries:
        dates, new_c, new_d, tot_c, tot_d = make_country_series(start, days, seed)
        df = pd.DataFrame({
            "iso_code": iso,
            "continent": continent,
            "location": name,
            "date": dates,
            "population": population,
            "total_cases": tot_c,
            "new_cases": new_c,
            "total_deaths": tot_d,
            "new_deaths": new_d,
            "total_tests": np.nan,
            "new_tests": np.nan,
            "total_vaccinations": np.nan,
            "people_vaccinated": np.nan,
            "people_fully_vaccinated": np.nan,
            "new_vaccinations": np.nan,
            "stringency_index": np.nan,
        })

        scale = 100_000
        pop = population
        df["total_cases_per_100k"] = (df["total_cases"] / pop) * scale
        df["total_deaths_per_100k"] = (df["total_deaths"] / pop) * scale
        df["new_cases_per_100k"] = (df["new_cases"] / pop) * scale
        df["new_deaths_per_100k"] = (df["new_deaths"] / pop) * scale

        frames.append(df)

    return pd.concat(frames, ignore_index=True)


def main() -> None:
    ensure_data_dir()
    df = build_sample_dataframe()
    df.to_parquet(OUTPUT, index=False)
    print(f"Sample dataset written to {OUTPUT}")


if __name__ == "__main__":
    main()


