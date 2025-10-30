import os
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime


st.set_page_config(page_title="COVID-19 Spread Patterns", layout="wide")

DATA_PATH = os.path.join("data", "covid_processed.parquet")


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        st.error("Processed data not found. Please run: python scripts/fetch_data.py")
        st.stop()
    df = pd.read_parquet(path)
    return df


def layout_header(df: pd.DataFrame) -> None:
    st.title("Visualization and Analysis of COVID-19 Spread Patterns")
    st.caption("Data source: Our World in Data")
    last_dt = pd.to_datetime(df["date"].max())
    st.write(f"Last data date: {last_dt.date()}")


def sidebar_controls(df: pd.DataFrame):
    continents = ["All"] + sorted([c for c in df["continent"].dropna().unique()])
    continent = st.sidebar.selectbox("Continent", continents)

    if continent != "All":
        subset = df[df["continent"] == continent]
    else:
        subset = df

    countries = sorted(subset["location"].unique())
    country = st.sidebar.selectbox("Country", countries, index=countries.index("United States") if "United States" in countries else 0)

    metric = st.sidebar.selectbox(
        "Time-series metric",
        [
            "new_cases",
            "new_deaths",
            "new_cases_per_100k",
            "new_deaths_per_100k",
        ],
        index=2,
    )

    map_metric = st.sidebar.selectbox(
        "Map metric (latest)",
        [
            "total_cases",
            "total_deaths",
            "total_cases_per_100k",
            "total_deaths_per_100k",
        ],
        index=2,
    )

    return continent, country, metric, map_metric


def render_country_timeseries(df: pd.DataFrame, country: str, metric: str) -> None:
    cdf = df[df["location"] == country].sort_values("date")
    fig = px.line(
        cdf,
        x="date",
        y=metric,
        title=f"{country} — {metric}",
        labels={"date": "Date", metric: metric.replace("_", " ").title()},
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_country_summary(df: pd.DataFrame, country: str) -> None:
    latest = (
        df[df["location"] == country]
        .sort_values("date")
        .tail(1)
        .squeeze()
    )
    def safe_int_str(value: float | int | None) -> str:
        try:
            if value is None:
                return "0"
            if pd.isna(value):
                return "0"
            return f"{int(value):,}"
        except Exception:
            return "0"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total cases", safe_int_str(latest.get("total_cases", 0)))
    c2.metric("Total deaths", safe_int_str(latest.get("total_deaths", 0)))
    c3.metric("People vaccinated", safe_int_str(latest.get("people_vaccinated", 0)))
    c4.metric("People fully vaccinated", safe_int_str(latest.get("people_fully_vaccinated", 0)))


def render_map(df: pd.DataFrame, metric: str) -> None:
    # Take latest per country
    latest_by_country = (
        df.sort_values("date")
        .groupby("iso_code", as_index=False)
        .tail(1)
    )
    # Some rows might be missing metric values; keep them but they’ll show as blank
    fig = px.choropleth(
        latest_by_country,
        locations="iso_code",
        color=metric,
        hover_name="location",
        color_continuous_scale="Reds",
        title=f"Global map — {metric} (latest)",
        projection="natural earth",
    )
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    df = load_data(DATA_PATH)
    layout_header(df)

    continent, country, metric, map_metric = sidebar_controls(df)

    # Filter on continent for global views (map) if selected
    if continent != "All":
        df_view = df[df["continent"] == continent]
    else:
        df_view = df

    with st.container():
        render_country_summary(df, country)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        render_country_timeseries(df, country, metric)
    with c2:
        render_map(df_view, map_metric)


if __name__ == "__main__":
    main()


