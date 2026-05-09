import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.database import get_inventory_history, get_shelf_health_history, get_product_list

st.set_page_config(page_title="Inventory", page_icon="📊", layout="wide")

st.title("📊 Inventory Dashboard")
st.markdown("View historical stock levels, trends, and shelf health over time.")

inv_df    = get_inventory_history()
health_df = get_shelf_health_history()

if inv_df.empty:
    st.info("No inventory data yet. Go to Detection page, scan a shelf, and save the results.")
    st.stop()

st.subheader("📌 Current Summary")

latest_scan = inv_df.sort_values("timestamp").groupby("product_name").last().reset_index()

total_products  = len(latest_scan)
critical_count  = len(latest_scan[latest_scan["status"] == "Critical"])
low_stock_count = len(latest_scan[latest_scan["status"] == "Low Stock"])
normal_count    = len(latest_scan[latest_scan["status"] == "Normal"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Products Tracked", total_products)
c2.metric("🟢 Normal",    normal_count)
c3.metric("🟡 Low Stock", low_stock_count)
c4.metric("🔴 Critical",  critical_count)

st.markdown("---")

st.subheader("📋 Latest Stock Status")

def color_status(val):
    if val == "Critical":
        return "background-color: #ffcccc"
    elif val == "Low Stock":
        return "background-color: #fff3cc"
    else:
        return "background-color: #ccffcc"

styled = latest_scan[["product_name", "detected_count", "threshold", "status", "timestamp"]]\
    .rename(columns={
        "product_name"  : "Product",
        "detected_count": "Count",
        "threshold"     : "Threshold",
        "status"        : "Status",
        "timestamp"     : "Last Updated"
    })\
    .style.map(color_status, subset=["Status"])

st.dataframe(styled, use_container_width=True)

st.markdown("---")

st.subheader("📈 Stock Level Trends")

products = get_product_list()
selected = st.multiselect(
    "Select products to display",
    options=products,
    default=products[:3] if len(products) >= 3 else products
)

if selected:
    trend_df = inv_df[inv_df["product_name"].isin(selected)].copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"])

    fig = px.line(
        trend_df,
        x="timestamp",
        y="detected_count",
        color="product_name",
        markers=True,
        title="Detected Count Over Time",
        labels={
            "detected_count": "Count",
            "timestamp"     : "Time",
            "product_name"  : "Product"
        }
    )

    fig.update_layout(
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
        legend_title_text="Product"
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("🏥 Shelf Health Score History")

if health_df.empty:
    st.info("No shelf health data recorded yet.")
else:
    health_df["timestamp"] = pd.to_datetime(health_df["timestamp"])

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=health_df["timestamp"],
        y=health_df["shelf_health_score"] * 100,
        mode="lines+markers",
        name="Health Score (%)",
        line=dict(color="#2ecc71", width=2),
        fill="tozeroy",
        fillcolor="rgba(46, 204, 113, 0.1)"
    ))

    fig2.add_hline(y=70, line_dash="dash", line_color="orange",
                   annotation_text="Good threshold (70%)")
    fig2.add_hline(y=40, line_dash="dash", line_color="red",
                   annotation_text="Critical threshold (40%)")

    fig2.update_layout(
        title="Shelf Health Score Over Time",
        yaxis_title="Health Score (%)",
        xaxis_title="Timestamp",
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0, 105])
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Score Component Breakdown")
    latest_health = health_df.sort_values("timestamp").iloc[-1]

    bc1, bc2, bc3 = st.columns(3)
    bc1.metric("Availability (×0.5)",       f"{latest_health['availability_score'] * 100:.0f}%")
    bc2.metric("Placement Accuracy (×0.3)", f"{latest_health['placement_score'] * 100:.0f}%")
    bc3.metric("Restock Efficiency (×0.2)", f"{latest_health['restock_efficiency'] * 100:.0f}%")

st.markdown("---")

with st.expander("🔍 View Raw Inventory Log"):
    st.dataframe(inv_df, use_container_width=True)