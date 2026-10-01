import pandas as pd
import numpy as np
import yaml
import os
from datetime import datetime

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def load_data(data_path):
    df = pd.read_csv(data_path)
    print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def check_required_columns(df, required_columns):
    missing_cols = [col for col in required_columns if col not in df.columns]
    return missing_cols

def clean_text_and_missing(df, config):
    strategy = config["missing_value_strategy"]
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if strategy.get("numeric_columns") == "median":
                df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(strategy.get("text_columns", "Unknown"))
            df[col] = df[col].astype(str).str.strip().str.title()
    return df

def remove_duplicates(df, key_columns):
    before = len(df)
    df = df.drop_duplicates(subset=key_columns)
    removed = before - len(df)
    print(f"Removed {removed} duplicate rows (based on {key_columns})")
    return df, removed

def fix_dates(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def check_numeric_ranges(df, range_checks):
    violations = {}
    for col, bounds in range_checks.items():
        if col in df.columns:
            bad_rows = df[(df[col] < bounds["min"]) | (df[col] > bounds["max"])]
            violations[col] = len(bad_rows)
    return violations

def calculate_quality_score(df, missing_before, duplicates_removed, range_violations, total_rows_before):
    total_cells = total_rows_before * df.shape[1]
    missing_penalty = (sum(missing_before.values()) / total_cells) * 40 if total_cells > 0 else 0
    duplicate_penalty = (duplicates_removed / total_rows_before) * 30 if total_rows_before > 0 else 0
    violation_penalty = (sum(range_violations.values()) / total_rows_before) * 30 if total_rows_before > 0 else 0
    score = 100 - missing_penalty - duplicate_penalty - violation_penalty
    return max(0, round(score, 1))

def log_quality_history(dataset_name, score, log_path="history/quality_log.csv"):
    os.makedirs("history", exist_ok=True)
    entry = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dataset_name": dataset_name,
        "quality_score": score
    }])
    if os.path.exists(log_path):
        entry.to_csv(log_path, mode="a", header=False, index=False)
    else:
        entry.to_csv(log_path, mode="w", header=True, index=False)
    print(f"Quality score {score}% logged to {log_path}")

def run_dataguard(data_path, config_path):
    config = load_config(config_path)
    df = load_data(data_path)
    total_rows_before = len(df)

    missing_cols = check_required_columns(df, config["required_columns"])
    if missing_cols:
        print(f"CRITICAL: Missing required columns: {missing_cols}")
        print("Stopping - fix the data source before proceeding.")
        return

    missing_before = df.isnull().sum().to_dict()

    df = clean_text_and_missing(df, config)
    df, duplicates_removed = remove_duplicates(df, config["duplicate_check_columns"])
    df = fix_dates(df, config["date_columns"])

    range_violations = check_numeric_ranges(df, config["numeric_range_checks"])

    score = calculate_quality_score(df, missing_before, duplicates_removed, range_violations, total_rows_before)
    log_quality_history(config["dataset_name"], score)

    if score < config["quality_threshold"]:
        print(f"ALERT: Quality score {score}% is below threshold {config['quality_threshold']}%")
    else:
        print(f"Quality score {score}% meets threshold")

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/cleaned_output.csv", index=False)
    print("Cleaned data saved to data/cleaned_output.csv")

    return df, score

if __name__ == "__main__":
    run_dataguard("data/raw_data.csv", "config/rules.yaml")