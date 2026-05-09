import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

def prepare_rf_features(df: pd.DataFrame):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["weekday"] = df["timestamp"].dt.weekday
    df["month"] = df["timestamp"].dt.month
    df["row_number"] = range(len(df))

    le = LabelEncoder()
    df["product_encoded"] = le.fit_transform(df["product_name"])
    return df, le

def forecast_random_forest(df: pd.DataFrame, product_name: str, steps: int = 7):
    product_df = df[df["product_name"] == product_name].copy()

    if len(product_df) < 5:
        return None, f"Not enough data for '{product_name}'. Need at least 5 records."
    
    product_df, le = prepare_rf_features(product_df)

    features_cols = ["hour", "day", "weekday", "month", "row_number"]
    X = product_df[features_cols]
    y = product_df["detected_count"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    last_row = product_df.iloc[-1]
    future_rows = []
    for i in range(1, steps+1):
        future_rows.append({
            "hour" : last_row["hour"],
            "day" : (last_row["day"] + i) % 28 + 1,
            "weekday" : (last_row["weekday"] + i) % 7,
            "month" : last_row["month"],
            "row_number" : last_row["row_number"] + i
        })
    future_df = pd.DataFrame(future_rows)
    predictions = model.predict(future_df)
    predictions = np.clip(predictions, 0, None).round().astype(int)

    forecast_df = pd.DataFrame({
        "step" : range(1, steps+1),
        "predicted_count" : predictions
    })
    return forecast_df, "success"

def forecast_arima(df: pd.DataFrame, product_name: str, steps: int = 7):
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        return None, "statsmodels not installed. Run: pip install statsmodels"
    product_df = df[df["product_name"] == product_name].copy()

    if len(product_df) < 8:
        return None, f"Not enough data for ARIMA on '{product_name}'. Need at least 8 records."
    
    product_df["timestamp"] = pd.to_datetime(product_df["timestamp"])
    product_df = product_df.sort_values("timestamp")
    series = product_df["detected_count"].values.astype(float)

    try:
        model = ARIMA(series, order=(1,1,1))
        result = model.fit()
        forecast = result.forecast(steps=steps)
        forecast = np.clip(forecast, 0, None).round().astype(int)

    except Exception as e:
        return None, f"ARIMA error: {str(e)}"
    
    forecast_df = pd.DataFrame({
        "step" : range(1, steps+1),
        "predicted_count" : forecast
    })
    return forecast_df, "success"

def generate_restock_recommendation(
        product_counts: dict,
        thresholds: dict,
        forecast_df: pd.DataFrame = None        
) -> list:
    recommendations = []
    for product, count in product_counts.items():
        threshold = thresholds.get(product, 5)

        if count == 0:
            urgency     = "🔴 CRITICAL"
            reorder_qty = threshold * 3
        elif count < threshold:
            urgency     = "🟡 LOW STOCK"
            reorder_qty = threshold * 2 - count
        else:
            urgency     = "🟢 NORMAL"
            reorder_qty = 0

        if forecast_df is not None and not forecast_df.empty:
            avg_future = forecast_df["predicted_count"].mean()
            if avg_future < threshold:
                reorder_qty = max(reorder_qty, int(threshold - avg_future) + threshold)

        recommendations.append({
            "product" : product,    
            "current" : count,
            "threshold" : threshold,
            "urgency" : urgency,
            "reorder_qty" : reorder_qty
        })
    return recommendations