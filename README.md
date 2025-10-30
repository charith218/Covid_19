# Visualization and Analysis of COVID-19 Spread Patterns

This project provides data ingestion, exploratory analysis, and an interactive dashboard to visualize COVID-19 spread patterns using the Our World in Data (OWID) dataset.

## Features
- Data fetch and processing from OWID
- Time-series analysis by country/region
- Comparative metrics (cases, deaths, tests, vaccinations)
- Interactive Streamlit dashboard with Plotly charts and a global choropleth map

## Project Structure

```
.
├─ app/
│  └─ streamlit_app.py
├─ data/                # Downloaded and processed data (gitignored)
├─ notebooks/
│  └─ EDA.ipynb
├─ scripts/
│  └─ fetch_data.py
├─ requirements.txt
└─ README.md
```

## Quickstart (Windows, no virtual environment)

1) Install dependencies globally for your user
```
pip install --user -r requirements.txt
```

2) Fetch and process data
```
python scripts/fetch_data.py
```

3) Run the dashboard
```
streamlit run app/streamlit_app.py
```

Then open the URL shown in the terminal (typically `http://localhost:8501`).

## Data Source
- Our World in Data COVID-19 dataset: `https://covid.ourworldindata.org/data/owid-covid-data.csv`

## Notes
- Some visualizations aggregate latest available data; others show time-series trends.
- The dataset is updated frequently by OWID; rerun the fetch script to get the latest data.

## Uploading to GitHub
1) Initialize git (inside this project folder)
```
git init
git add .
git commit -m "Initial commit: COVID-19 visualization project"
```

2) Create a new repository on GitHub (via the website), then connect and push
```
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

This repo already includes a `.gitignore` that excludes the `data/` directory so large datasets are not pushed.
