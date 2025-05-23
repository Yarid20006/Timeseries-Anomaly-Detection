import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from anomaly_detection import detect_anomalies
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter


st.set_page_config(page_title="Time Series Anomaly Detection", layout="wide")
st.markdown("""
  <style>
    #MainMenu, footer, [data-testid="stSidebar"] {visibility:hidden;}
  </style>
""", unsafe_allow_html=True)


def run_detection():
    df = st.session_state["uploaded_df"]
    anomalies, hourly, stl = detect_anomalies(df)
    st.session_state["anomalies"] = anomalies
    st.session_state["hourly"]    = hourly
    st.session_state["stl"]       = stl


def reset_app():
    for key in ["anomalies", "hourly", "stl", "uploaded_df", "uploaded_file"]:
        st.session_state.pop(key, None)


if "anomalies" not in st.session_state:
    st.title("Time Series Anomaly Detection")
    uploaded = st.file_uploader(
        "Upload your time series CSV file",
        type=["csv"],
        key="uploaded_file"
    )

    if uploaded is None:
        st.stop()

    df = pd.read_csv(uploaded)
    st.session_state["uploaded_df"] = df

    st.success("File uploaded successfully")
    st.dataframe(df.head())
    st.button("Run Anomaly Detection", on_click=run_detection)
    st.stop()


st.title("Time Series Anomaly Detection")
st.button("Upload New File", on_click=reset_app)
st.success("Detection completed")

anomalies = st.session_state["anomalies"]
hourly    = st.session_state["hourly"]
stl       = st.session_state["stl"]

capitalize_methods = {
    "zscore":      "Z‑score",
    "iforest":     "Isolation Forest",
    "changepoint": "Change point",
}

for a in anomalies:
    ts       = a["timestamp"]
    date_str = ts.strftime("%Y-%m-%d")
    time_str = ts.strftime("%H:%M:%S")
    label    = a["type"] + " anomaly"
    conf_str = f"{int(a['confidence']*100)}% confidence"
    methods  = ", ".join(capitalize_methods[m] for m in a["methods"])

    st.markdown(
        f"**Date:** {date_str}   •   **Time:** {time_str}   —   **{label}**   ({conf_str})"
    )
    st.markdown(f"**Methods:** {methods}")

    with st.expander("See details"):
        t0 = ts - pd.Timedelta(hours=48)
        t1 = ts + pd.Timedelta(hours=48)
        sub = hourly[(hourly["Start Time"] >= t0) & (hourly["Start Time"] <= t1)]

        trend    = stl.trend
        seasonal = stl.seasonal
        resid    = stl.resid

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(sub["Start Time"], sub["y"] / 1e8, label="Original")
        ax.plot(sub["Start Time"], trend[sub.index] / 1e8, label="Trend")
        ax.plot(sub["Start Time"], seasonal[sub.index] / 1e8, label="Seasonal")
        ax.plot(sub["Start Time"], resid[sub.index] / 1e8, label="Residual")
        ax.axvline(ts, color="red", linestyle="--", label="Anomaly")

        ax.set_xlabel("Timestamp (MM-DD, HH:MM)", fontsize=10)
        ax.set_ylabel("Aggregated Value (×10⁸)", fontsize=10)
        ax.set_title(f"Anomaly details: {label}", fontsize=12, fontweight="bold")
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d, %H:%M"))
        fig.autofmt_xdate(rotation=30)

        ax.legend()
        st.pyplot(fig)

