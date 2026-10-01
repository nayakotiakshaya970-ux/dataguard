import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="DataGuard Dashboard", layout="centered")
st.title("🛡️ DataGuard — Data Quality Monitoring")

log_path = "history/quality_log.csv"

if os.path.exists(log_path):
    log_df = pd.read_csv(log_path)
    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])

    st.subheader("Quality Score Over Time")
    st.line_chart(log_df.set_index("timestamp")["quality_score"])

    latest_score = log_df["quality_score"].iloc[-1]
    st.metric("Latest Quality Score", f"{latest_score}%")

    if latest_score < 80:
        st.error("⚠️ Data quality is below the acceptable threshold (80%)")
    else:
        st.success("✅ Data quality is healthy")

    st.subheader("Full History")
    st.dataframe(log_df, use_container_width=True)
else:
    st.warning("No quality history yet. Run dataguard.py first to generate data.")