import streamlit as st, pandas as pd, matplotlib.pyplot as plt

st.set_page_config(page_title="Anomaly details", layout="wide")
st.title("Anomaly details")

if "selected" not in st.session_state:
    st.error("No anomaly selected"); st.stop()

sel = st.session_state["selected"]
st.write(f"**Type:** {sel['type']}   **Confidence:** {sel['confidence']*100:.0f}%")

df = st.session_state["df"]
time_col = st.session_state["time_col"]; val_col = st.session_state["value_col"]

trend = pd.Series(st.session_state["stl_trend"], index=df.index)
season = pd.Series(st.session_state["stl_seasonal"], index=df.index)
resid  = pd.Series(st.session_state["stl_resid"], index=df.index)

anom_t = sel["timestamp"]; anom_type = sel["type"]
st.write(f"**Type:** {anom_type} &nbsp;&nbsp; **Time:** {anom_t}")


win = pd.Timedelta(hours=48)
mask = (df[time_col] >= anom_t - win) & (df[time_col] <= anom_t + win)
sub = df.loc[mask].copy()
sub["trend"], sub["seasonal"], sub["resid"] = trend[mask], season[mask], resid[mask]

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(sub[time_col], sub[val_col], label="original")
ax.plot(sub[time_col], sub["trend"], label="trend")
ax.plot(sub[time_col], sub["seasonal"], label="seasonal")
ax.plot(sub[time_col], sub["resid"], label="residual")
ax.axvline(anom_t, color="red", linestyle="--", label="anomaly")
ax.set_xlabel("time"); ax.set_ylabel(val_col); ax.legend()
st.pyplot(fig)

if st.button("Back"):
    st.switch_page("home")

