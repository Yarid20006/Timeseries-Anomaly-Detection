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
    iso_cont=0.005,
    max_cp=15,
):
    # fast parse
    if df[time_col].dtype == "object":
        df[time_col] = pd.to_datetime(df[time_col], format=fmt, errors="coerce")

    # hourly aggregate to cut rows 95%
    hourly = (
        df.set_index(time_col)
          .resample("1h")[value_col]
          .sum()
          .rename("y")
          .to_frame()
          .dropna()
          .reset_index()
    )

    # 1) STL + Z‑score
    stl = STL(hourly["y"], period=24).fit()
    resid = stl.resid
    z = zscore(resid, nan_policy="omit")
    spike_m = np.abs(z) > z_thr
    spike_lbl = np.where(resid > 0, "spike", "drop")

    # 2) Isolation Forest
    iso = IsolationForest(
        contamination=iso_cont,
        max_samples=5000,
        n_estimators=150,
        n_jobs=-1,
        random_state=42,
    )
    scores = -iso.fit(hourly[["y"]]).score_samples(hourly[["y"]])
    thr = np.percentile(scores, 100 * (1 - iso_cont))
    iso_m = scores > thr

    # 3) BinSeg change‑point
    bs = rpt.Binseg(model="l2").fit(hourly["y"].values)
    bkps = bs.predict(n_bkps=max_cp)
    cp_m = np.zeros(len(hourly), bool)
    cp_m[bkps[:-1]] = True

    anomalies, seen = [], set()
    for i, ts in enumerate(hourly[time_col]):
        votes = []
        if spike_m[i]:
            votes.append("zscore")
        if iso_m[i]:
            votes.append("iforest")
        if cp_m[i]:
            votes.append("changepoint")

        # loosened: any 2 of the 3
        if len(votes) >= 1 and ts not in seen:
            # decide type by majority
            if "changepoint" in votes:
                 a_type = "Collective"

            elif "zscore" in votes:
                 a_type = "Contextual"
            else:
                 a_type = "Point"

            anomalies.append({
                "timestamp": ts,
                "type": a_type,
                "confidence": round(len(votes) / 3, 2),
                "methods": votes.copy()
            })
            seen.add(ts)


    return anomalies, hourly, stl
