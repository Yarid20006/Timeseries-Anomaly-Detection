
import pandas as pd
from statsmodels.tsa.seasonal import STL
import numpy as np
from scipy.stats import zscore

def detect_anomalies(df, time_col, value_col, z_thresh=3, window_size=10):
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col).reset_index(drop=True)

    df[value_col] = df[value_col].interpolate()


    stl = STL(df[value_col], period=24) 
    result = stl.fit()
    residuals = result.resid

    residual_z = zscore(residuals)
    contextual_mask = np.abs(residual_z) > z_thresh

    rolling_std = df[value_col].rolling(window=window_size).std()
    std_diff = rolling_std.diff().abs()
    collective_mask = std_diff > std_diff.mean() + 2 * std_diff.std()

    anomalies = []
    for idx in df.index:
        if contextual_mask[idx]:
            anomalies.append({
                "timestamp": df[time_col][idx],
                "type": "Contextual",
                "confidence": min(1.0, abs(residual_z[idx]) / 5)
            })
        elif collective_mask[idx]:
            anomalies.append({
                "timestamp": df[time_col][idx],
                "type": "Collective",
                "confidence": min(1.0, std_diff[idx] / (std_diff.std() + 1e-5))
            })

    return anomalies
