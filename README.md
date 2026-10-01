# DataGuard — Configurable Data Quality Monitoring Framework

## Problem
Teams rewrite custom cleaning scripts for every new dataset, and no one
tracks whether data quality is improving or degrading over time — issues
are only caught after they break downstream reports.

## Solution
A configuration-driven pipeline (rules defined in YAML, not code) that:
- Validates required columns exist before processing
- Cleans missing values, duplicates, and dates
- Checks business rules (e.g., valid numeric ranges)
- Calculates a single 0-100 data quality score
- Logs quality score history over time and alerts if it drops below threshold

## How to run
pip install -r requirements.txt
python dataguard.py
streamlit run app.py

## Tech stack
Python, Pandas, YAML, Streamlit

## Future improvements
- Email/Slack alerts instead of console warnings
- Support for multiple datasets tracked in parallel
- Integration with real data pipelines (Airflow, dbt)