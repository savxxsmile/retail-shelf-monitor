import streamlit as st
import sys 
import os

sys.path.append(os.path.dirname(__file__))

from utils.database import init_db

init_db()

st.set_page_config(
    page_title = "AI Retail Shelf Monitor",
    page_icon = "🛒",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

st.title("🛒 AI-Powered Retail Shelf Monitoring & Smart Restocking System")
st.markdown("**Sadhvi Singh**")
st.markdown("___")

st.markdown("""
            ### Welcome to the Project Dashboard
            
This system integrates **Computer Vision** and **Predicitve Analytics** to automate retail inventory management. Navigate using the sidebar to access each module.
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    #### 📷 Detection Module
    - Upload shelf images
    - Auto-detect and count products using **YOLOv8 nano**
    - Validate planogram compliance
    - Compute **Shelf Health Score**
    - Save results to database
                
    #### 📊 Inventory Dashboard
    - View historical stock levels
    - Monitor stock status (Normal/ Low/ Critical)
    - Track Shelf Health Score over time
                
    ### 🏗️ System Architecture (4-Layer)
    | Layer | Name | Components |
    |-------|------|------------|
    | 1 | Image Acquisition | OpenCV preprocessing, image upload |
    | 2 | Product Detection | YOLOv8 nano, bounding boxes, counting |
    | 3 | Inventory Analytics | SQLite, planogram validation, Shelf Health Score |
    | 4 | Forecasting & Recommendation | Random Forest / ARIMA, restock suggestions |
                
    """)
    
with col2:
    st.markdown("""
    #### 🔮 Forecasting Module
    - Predict future demand using **Random Forest** or **ARIMA**
    - Estimate stock-out dates
    - Generate **smart restocking recommendations**
                
    #### 📋 Planogram Setup
    - Define expected shelf layout
    - Set minimum stock thresholds per product
    - Manage product categories
                
    ### 📐 Shelf Health Score Formula
    ```python
    Shelf Health Score = (Availability × 0.5) + (Placement Accuracy × 0.3) + (Restock Efficiency × 0.2) 
    ```
                
    ### 🚀 Getting Started
    1. Go to **📷 Detection** → upload a shelf image → run detection → save
    2. Go to **📊 Inventory** → view stock trends and health scores
    3. Go to **🔮 Forecast** → predict demand and get restock recommendations
    4. Go to **📋 Planogram** → define expected shelf layout
    """)

    

    st.markdown("---")
    st.caption("Built with Python · YOLOv8 · Streamlit · SQLite · Scikit-learn · Statsmodels")