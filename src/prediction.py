"""
prediction.py — Simple LinearRegression to predict average book price for the next page.
This is an academic feature using page_number as a pseudo-time axis.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_next_page_price(df: pd.DataFrame) -> dict:
    """
    Groups books by page_number, computes average price per page,
    fits a LinearRegression, and predicts the next page's avg price.

    Returns a dict with:
        page_avg_df   — DataFrame(page_number, avg_price)
        next_page     — int
        predicted_price — float
        slope         — float
        trend         — str: 'Increasing', 'Decreasing', or 'Stable'
        r2            — float (model R²)
        success       — bool
        message       — str
    """
    result = {
        "page_avg_df": pd.DataFrame(),
        "next_page": None,
        "predicted_price": None,
        "slope": None,
        "trend": None,
        "r2": None,
        "success": False,
        "message": "",
    }

    if df.empty or "page_number" not in df.columns:
        result["message"] = "No data available for prediction."
        return result

    page_avg = (
        df.groupby("page_number")["price"]
        .mean()
        .reset_index()
        .rename(columns={"price": "avg_price"})
        .sort_values("page_number")
    )

    if len(page_avg) < 2:
        result["message"] = "Need at least 2 pages of data for prediction."
        result["page_avg_df"] = page_avg
        return result

    X = page_avg["page_number"].values.reshape(-1, 1)
    y = page_avg["avg_price"].values

    model = LinearRegression()
    model.fit(X, y)

    next_page = int(page_avg["page_number"].max()) + 1
    predicted_price = float(model.predict([[next_page]])[0])
    slope = float(model.coef_[0])
    r2 = float(model.score(X, y))

    if slope > 0.05:
        trend = "Increasing"
    elif slope < -0.05:
        trend = "Decreasing"
    else:
        trend = "Stable"

    result.update({
        "page_avg_df": page_avg,
        "next_page": next_page,
        "predicted_price": round(predicted_price, 2),
        "slope": round(slope, 4),
        "trend": trend,
        "r2": round(r2, 4),
        "success": True,
        "message": "Prediction computed successfully.",
    })
    return result
