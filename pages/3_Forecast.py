import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.database    import get_inventory_history, get_product_list
from utils.forecasting import (forecast_random_forest, forecast_arima,
                                generate_restock_recommendation)

st.set_page_config(page_title="Forecast", page_icon="🔮", layout="wide")

st.title("🔮 Demand Forecast & Restock Recommendations")
st.markdown("Predict future stock levels and get smart restocking suggestions.")

inv_df   = get_inventory_history()
products = get_product_list()

if inv_df.empty or not products:
    st.info("No inventory data yet. Scan at least one shelf from the Detection page first.")
    st.stop()

st.markdown("---")

with st.sidebar:
    st.header("🔧 Forecast Settings")
    model_choice  = st.radio("Forecasting Model", ["Random Forest", "ARIMA"])
    forecast_days = st.slider("Forecast Steps", 3, 30, 7)
    st.markdown("---")
    st.caption("Random Forest: better for irregular data\nARIMA: better for consistent sales patterns")

st.subheader("📦 Select Product to Forecast")
selected_product = st.selectbox("Choose a product", products)

if st.button("🚀 Run Forecast", type="primary"):
    with st.spinner(f"Running {model_choice} forecast for '{selected_product}'..."):
        if model_choice == "Random Forest":
            forecast_df, msg = forecast_random_forest(inv_df, selected_product, steps=forecast_days)
        else:
            forecast_df, msg = forecast_arima(inv_df, selected_product, steps=forecast_days)

    if forecast_df is None:
        st.error(f"Forecast failed: {msg}")
    else:
        st.success(f"Forecast complete using {model_choice}!")

        st.subheader(f"📈 Forecast: {selected_product}")

        hist = inv_df[inv_df["product_name"] == selected_product].copy()
        hist["timestamp"] = pd.to_datetime(hist["timestamp"])
        hist = hist.sort_values("timestamp")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(range(len(hist))),
            y=hist["detected_count"].tolist(),
            mode="lines+markers",
            name="Historical",
            line=dict(color="#3498db", width=2)
        ))

        offset = len(hist)
        fig.add_trace(go.Scatter(
            x=list(range(offset, offset + len(forecast_df))),
            y=forecast_df["predicted_count"].tolist(),
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#e74c3c", width=2, dash="dash"),
            marker=dict(symbol="diamond")
        ))

        threshold = hist["threshold"].iloc[-1] if "threshold" in hist.columns else 5

        fig.add_hline(
            y=threshold,
            line_dash="dot",
            line_color="orange",
            annotation_text=f"Min threshold ({threshold})"
        )

        fig.update_layout(
            title=f"Stock Forecast: {selected_product}",
            xaxis_title="Time Steps",
            yaxis_title="Detected Count",
            plot_bgcolor ="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h")
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 View Forecast Data"):
            st.dataframe(forecast_df, use_container_width=True)

        below_threshold = forecast_df[forecast_df["predicted_count"] < threshold]

        if not below_threshold.empty:
            first_low = below_threshold.iloc[0]["step"]
            st.warning(f"⚠️ '{selected_product}' is predicted to fall below threshold at step {first_low}. Consider restocking soon!")
        else:
            st.success(f"✅ '{selected_product}' is predicted to stay above threshold for all {forecast_days} steps.")

        st.session_state["forecast_df"]      = forecast_df
        st.session_state["forecast_product"] = selected_product

st.markdown("---")

st.subheader("🛒 Restock Recommendations")
st.markdown("Based on current detected counts from the most recent scan.")

latest         = inv_df.sort_values("timestamp").groupby("product_name").last().reset_index()
product_counts = dict(zip(latest["product_name"], latest["detected_count"]))
thresholds     = dict(zip(latest["product_name"], latest["threshold"]))

forecast_df_for_recs = st.session_state.get("forecast_df", None)

recommendations = generate_restock_recommendation(product_counts, thresholds, forecast_df_for_recs)

for rec in recommendations:
    with st.container():
        rcol1, rcol2, rcol3, rcol4 = st.columns([2, 1, 1, 2])
        rcol1.markdown(f"**{rec['product']}**")
        rcol2.markdown(f"Current: `{rec['current']}`")
        rcol3.markdown(f"Min: `{rec['threshold']}`")
        rcol4.markdown(rec["urgency"])

        if rec["reorder_qty"] > 0:
            st.info(f"➡️ Recommended reorder quantity: **{rec['reorder_qty']} units**")

        st.markdown("---")