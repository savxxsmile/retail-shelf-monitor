import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.planogram import load_planogram, save_planogram
from utils.database  import get_product_list

st.set_page_config(page_title="Planogram", page_icon="📋", layout="wide")

st.title("📋 Planogram Setup")
st.markdown("Define the expected shelf layout — which products should be present and in what quantity.")

planogram = load_planogram()

st.subheader("Current Planogram")

if planogram:
    st.json(planogram)
else:
    st.info("No planogram defined yet.")

st.markdown("---")

st.subheader("✏️ Edit Planogram")

known_products = get_product_list()

if known_products:
    st.markdown("Products detected from previous scans are pre-loaded below:")
    new_planogram = {}
    cols = st.columns(3)

    for i, product in enumerate(known_products):
        with cols[i % 3]:
            qty = st.number_input(
                f"{product}",
                min_value=0, max_value=100,
                value=planogram.get(product, 5),
                step=1,
                key=f"plano_{product}"
            )
            if qty > 0:
                new_planogram[product] = qty

    if st.button("💾 Save Planogram", type="primary"):
        save_planogram(new_planogram)
        st.success("Planogram saved successfully!")
        st.json(new_planogram)

else:
    st.info("No products scanned yet. Run a detection first to populate the product list.")

st.markdown("---")

st.subheader("➕ Add Product Manually")

with st.form("add_product_form"):
    new_name  = st.text_input("Product Name (class label)")
    new_qty   = st.number_input("Expected Quantity", min_value=1, value=5)
    submitted = st.form_submit_button("Add to Planogram")

    if submitted and new_name:
        planogram[new_name] = new_qty
        save_planogram(planogram)
        st.success(f"Added '{new_name}' with expected quantity {new_qty}")

st.markdown("---")

if planogram and st.button("🗑️ Clear Planogram", type="secondary"):
    save_planogram({})
    st.warning("Planogram cleared.")
    st.rerun()