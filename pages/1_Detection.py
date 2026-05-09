import streamlit as st
import numpy as np
from PIL import Image
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.detection import load_model, run_detection, preprocess_image
from utils.database  import log_detection, log_shelf_health
from utils.planogram import (load_planogram, validate_planogram,
                              compute_availability_score,
                              create_default_planogram)

st.set_page_config(page_title="Detection", page_icon="📷", layout="wide")

st.title("📷 Shelf Detection & Monitoring")
st.markdown("Upload a shelf image to detect products, check stock levels, and validate planogram.")

with st.sidebar:
    st.header("⚙️ Settings")
    use_custom = st.toggle("Use Custom Trained Model (best.pt)", value=False)
    confidence = st.slider("Detection Confidence", 0.1, 0.9, 0.4, 0.05)
    st.markdown("---")
    st.caption("Custom model requires models/best.pt from Colab training.")

@st.cache_resource
def get_model(custom: bool):
    return load_model(use_custom=custom)

with st.spinner("Loading YOLO model..."):
    model = get_model(use_custom)

st.success(f"Model loaded: {'Custom best.pt' if use_custom else 'Pre-trained YOLOv8n'}")

uploaded = st.file_uploader(
    "Upload a shelf image",
    type=["jpg", "jpeg", "png"],
    help="Take a photo of your store shelf and upload it here."
)

if uploaded:
    col1, col2 = st.columns(2)

    image_np = preprocess_image(uploaded)

    with col1:
        st.subheader("Original Image")
        st.image(image_np, use_container_width=True)

    with st.spinner("Running detection..."):
        annotated, product_counts, detections, class_colors = run_detection(image_np, model, confidence)

    with col2:
        st.subheader("Detection Result")
        st.image(annotated, use_container_width=True)

        # Color legend — only show if more than one meaningful class detected
        generic_classes = {"object", "empty", "0", "1"}
        meaningful_colors = {
            cls: color for cls, color in class_colors.items()
            if cls.lower() not in generic_classes
        }

        if meaningful_colors:
            st.markdown("**🎨 Color Legend:**")
            legend_cols = st.columns(min(len(meaningful_colors), 4))
            for i, (cls, color) in enumerate(meaningful_colors.items()):
                hex_color = "#{:02x}{:02x}{:02x}".format(*color)
                with legend_cols[i % 4]:
                    st.markdown(
                        f'<div style="background-color:{hex_color}; '
                        f'padding:6px; border-radius:5px; '
                        f'color:white; text-align:center;">'
                        f'<b>{cls}</b></div>',
                        unsafe_allow_html=True
                    )

    st.markdown("---")

    st.subheader("📦 Detected Products")

    if not product_counts:
        st.warning("No products detected. Try lowering the confidence threshold.")
    else:
        st.markdown("**Set stock thresholds for each detected product:**")
        thresholds = {}
        cols = st.columns(min(len(product_counts), 4))

        for i, product in enumerate(product_counts):
            with cols[i % 4]:
                thresholds[product] = st.number_input(
                    f"Min for `{product}`",
                    min_value=1, max_value=50,
                    value=5, step=1,
                    key=f"thresh_{product}"
                )

        st.markdown("**Stock Status:**")
        status_cols = st.columns(min(len(product_counts), 4))

        for i, (product, count) in enumerate(product_counts.items()):
            threshold = thresholds[product]
            with status_cols[i % 4]:
                if count == 0:
                    st.error(f"🔴 **{product}**\nCount: {count}\n(CRITICAL)")
                elif count < threshold:
                    st.warning(f"🟡 **{product}**\nCount: {count}\n(LOW STOCK)")
                else:
                    st.success(f"🟢 **{product}**\nCount: {count}\n(NORMAL)")

        st.markdown("---")

        st.subheader("📋 Planogram Validation")
        planogram = load_planogram()

        if not planogram:
            st.info("No planogram set up yet.")
            if st.button("🔧 Auto-create planogram from detected products"):
                planogram = create_default_planogram(list(product_counts.keys()))
                st.success(f"Planogram created for: {list(planogram.keys())}")

        if planogram:
            validation = validate_planogram(product_counts, planogram)
            vcol1, vcol2, vcol3 = st.columns(3)

            with vcol1:
                st.metric("✅ Matched Products", len(validation["matched"]))
                if validation["matched"]:
                    st.write(", ".join(validation["matched"]))

            with vcol2:
                st.metric("❌ Missing Products", len(validation["missing"]))
                if validation["missing"]:
                    for m in validation["missing"]:
                        st.write(f"- {m}")

            with vcol3:
                st.metric("⚠️ Extra Products", len(validation["extra"]))
                if validation["extra"]:
                    for e in validation["extra"]:
                        st.write(f"- {e}")

            placement_score = validation["placement_score"]
            st.progress(placement_score, text=f"Placement Accuracy: {placement_score * 100:.0f}%")
        else:
            placement_score = 1.0

        st.markdown("---")

        st.subheader("🏥 Shelf Health Score")

        availability = compute_availability_score(product_counts, thresholds)
        restock_eff  = min(1.0, sum(product_counts.values()) / (len(product_counts) * 10))
        health_score = round((availability * 0.5) + (placement_score * 0.3) + (restock_eff * 0.2), 2)

        hcol1, hcol2, hcol3, hcol4 = st.columns(4)
        hcol1.metric("Availability",       f"{availability * 100:.0f}%",    help="Weight: 0.5")
        hcol2.metric("Placement Accuracy", f"{placement_score * 100:.0f}%", help="Weight: 0.3")
        hcol3.metric("Restock Efficiency", f"{restock_eff * 100:.0f}%",     help="Weight: 0.2")
        hcol4.metric("🏥 Health Score",    f"{health_score * 100:.0f}%")

        st.progress(health_score, text=f"Overall Shelf Health: {health_score * 100:.0f}%")

        st.markdown("---")

        if st.button("💾 Save Detection to Database", type="primary"):
            log_detection(product_counts, thresholds)
            log_shelf_health(availability, placement_score, restock_eff)
            st.success("✅ Detection data saved to database!")
            st.balloons()