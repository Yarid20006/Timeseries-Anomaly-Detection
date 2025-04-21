import pandas as pd, numpy as np, ruptures as rpt
from statsmodels.tsa.seasonal import STL
from scipy.stats import zscore
from sklearn.ensemble import IsolationForest

def detect_anomalies(
    df,
    time_col="Start Time",
    value_col="Trip Distance",
    fmt="%m/%d/%Y %I:%M:%S %p",
    z_thr=3.5,
    iso_cont=0.01,
    max_cp=15,            # ⬅ limit change‑points
):
    # ---------- fast datetime parse directly in read_csv ----------
    if df[time_col].dtype == "object":
        df[time_col] = pd.to_datetime(df[time_col], format=fmt, errors="coerce")

    # ---------- hourly aggregation ----------
    hourly = (
        df.set_index(time_col)
          .resample("1H")[value_col]
          .sum()
          .rename("y")
          .to_frame()
          .dropna()
          .reset_index()
    )

    # ---------- STL ----------
    stl = STL(hourly["y"], period=24).fit()
    resid = stl.resid
    z = zscore(resid, nan_policy="omit")
    spike_mask = np.abs(z) > z_thr
    spike_lbl = np.where(resid > 0, "spike", "drop")

    # ---------- Isolation Forest ----------
    iso = IsolationForest(
        contamination=iso_cont,
        max_samples=5000,
        n_estimators=150,
        n_jobs=-1,
        random_state=42,
    )
    iso_scores = -iso.fit(hourly[["y"]]).score_samples(hourly[["y"]])
    iso_thr = np.percentile(iso_scores, 100 * (1 - iso_cont))
    iso_mask = iso_scores > iso_thr

    # ---------- BinSeg change‑point ----------
    bs = rpt.Binseg(model="l2").fit(hourly["y"].values)
    cp_idx = bs.predict(n_bkps=max_cp)
    cp_mask = np.zeros(len(hourly), dtype=bool)
    cp_mask[cp_idx[:-1]] = True

    # ---------- voting ----------
    anomalies, seen = [], set()
    for i, ts in enumerate(hourly[time_col]):
        votes = []
        if spike_mask[i]:
            votes.append(spike_lbl[i])
        if iso_mask[i]:
            votes.append("iforest")
        if cp_mask[i]:
            votes.append("shift")
        if len(votes) >= 2 and ts not in seen:
            a_type = "shift" if "shift" in votes else ("spike" if "spike" in votes else "drop")
            confidence = round(len(votes) / 3, 2)
            anomalies.append({"timestamp": ts, "type": a_type, "confidence": confidence})
            seen.add(ts)

    return anomalies, hourly, stl
