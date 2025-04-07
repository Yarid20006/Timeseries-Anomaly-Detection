
import streamlit as st
import pandas as pd
from anomaly_detection import detect_anomalies

st.set_page_config(page_title="Time Series Anomaly Detection", layout="wide")

st.title("Time Series Anomaly Detection")
st.caption("Upload your time series CSV file")

uploaded_file = st.file_uploader("Drag and drop file here", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.success("File uploaded successfully:")
    st.dataframe(df.head())

    if st.button("Run Anomaly Detection"):
        with st.spinner("Running anomaly detection..."):
            anomalies = detect_anomalies(
                df,
                time_col="Start Time",
                value_col="Trip Distance"
            )

        st.success("Anomaly detection completed!")
        st.subheader("Detected Anomalies:")

        if not anomalies:
            st.info("No anomalies detected.")
        else:
            for a in anomalies:
                st.markdown(
                    f"<span style='color:#facc15'> {a['timestamp'].strftime('%Y-%m-%d %H:%M')}</span> — "
                    f"<b>{a['type']}</b> anomaly with <b>{a['confidence']*100:.1f}%</b> confidence",
                    unsafe_allow_html=True
                )
