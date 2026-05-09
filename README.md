# 🛒 AI-Powered Retail Shelf Monitoring & Smart Restocking System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)
![License](https://img.shields.io/badge/License-MIT-green)

> B.Tech Final Year Project | Sadhvi Singh | Roll No: 26163  
> Department of Computer Science and Engineering  
> Dronacharya College of Engineering, Gurugram University

---

## 📌 Project Overview

This system integrates **Computer Vision** and **Predictive Analytics** to automate
retail inventory management. It detects products from shelf images, monitors stock
levels, validates planogram compliance, and predicts future demand — all through
an interactive web dashboard.

---

## 🏗️ System Architecture (4-Layer)

Layer 1 — Image Acquisition → OpenCV preprocessing
Layer 2 — Product Detection → YOLOv8 nano/medium
Layer 3 — Inventory Analytics → SQLite + Planogram + Shelf Health Score
Layer 4 — Forecasting → Random Forest / ARIMA + Restock Recommendations

---

## ✨ Features

- 📷 **Real-time shelf image detection** using YOLOv8
- 📦 **Automatic product counting** with color-coded bounding boxes
- 📋 **Planogram validation** — detects misplaced and missing products
- 🏥 **Shelf Health Score** using weighted formula
- 📈 **Stock trend visualization** with interactive Plotly charts
- 🔮 **Demand forecasting** using Random Forest and ARIMA
- 🛒 **Smart restock recommendations** with urgency levels
- 💾 **SQLite database** for historical inventory tracking
- 🎨 **Class-based color coding** — same product always same color

---

## 📐 Shelf Health Score Formula

Score = (Availability × 0.5) + (Placement Accuracy × 0.3) + (Restock Efficiency × 0.2)

| Component          | Weight | Description                              |
| ------------------ | ------ | ---------------------------------------- |
| Availability       | 0.5    | Products meeting minimum stock threshold |
| Placement Accuracy | 0.3    | Planogram compliance                     |
| Restock Efficiency | 0.2    | Overall shelf fullness                   |

---

## 🛠️ Tech Stack

| Purpose           | Technology                |
| ----------------- | ------------------------- |
| Object Detection  | YOLOv8 (Ultralytics)      |
| Image Processing  | OpenCV                    |
| Dashboard         | Streamlit                 |
| Database          | SQLite                    |
| Data Analysis     | Pandas, NumPy             |
| Forecasting       | Scikit-learn, Statsmodels |
| Charts            | Plotly                    |
| Training Platform | Google Colab (T4 GPU)     |
| Dataset           | Roboflow Universe         |

---

## 📁 Project Structure

retail_shelf_monitor/
│
├── app.py ← Main Streamlit entry point
├── requirements.txt ← Python dependencies
├── README.md ← Project documentation
│
├── pages/
│ ├── 1_Detection.py ← Image upload + YOLOv8 detection
│ ├── 2_Inventory.py ← Stock history + trends dashboard
│ ├── 3_Forecast.py ← Demand forecast + restock advice
│ └── 4_Planogram.py ← Shelf layout setup
│
├── utils/
│ ├── init.py
│ ├── database.py ← SQLite operations
│ ├── detection.py ← YOLOv8 inference wrapper
│ ├── planogram.py ← Planogram validation logic
│ └── forecasting.py ← Random Forest + ARIMA
│
├── models/
│ └── best.pt ← Custom trained YOLOv8 weights
│
└── data/
├── inventory.db ← SQLite database (auto-created)
└── planogram/
└── planogram.json ← Shelf layout config

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.10 or higher
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/retail-shelf-monitor.git
cd retail-shelf-monitor
```

### Step 2 — Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🚀 How to Use

### Step 1 — Detection

1. Go to **📷 Detection** page
2. Upload a shelf image (JPG/PNG)
3. Set minimum stock thresholds per product
4. Click **Save Detection to Database**

### Step 2 — Inventory Dashboard

1. Go to **📊 Inventory** page
2. View stock status table and trend charts
3. Monitor Shelf Health Score over time

### Step 3 — Forecasting

1. Go to **🔮 Forecast** page
2. Select a product from the dropdown
3. Choose Random Forest or ARIMA model
4. Click **Run Forecast**
5. View restock recommendations below

### Step 4 — Planogram Setup

1. Go to **📋 Planogram** page
2. Set expected quantities per product
3. Save the planogram layout

---

## 🤝 Connecting Custom Trained Model

After training on Google Colab:

1. Download `best.pt` from `runs/detect/retail_shelf_model/weights/`
2. Place it in the `models/` folder
3. On Detection page → toggle **"Use Custom Trained Model"** → ON

---

## 📊 Model Training Results

| Metric    | Result |
| --------- | ------ |
| Precision | 0.6291 |
| Recall    | 0.5328 |
| mAP@0.5   | 0.5097 |
| F1-Score  | 0.5770 |

Training configuration:

- Model: YOLOv8 nano
- Dataset: Grocery Product Detection (Roboflow)
- Epochs: 30
- Image Size: 640×640
- GPU: Tesla T4 (Google Colab)
- Training Time: ~10 minutes

---

## 🔮 Future Scope

- Real-time CCTV streaming integration
- Multi-store deployment with cloud management
- POS system integration
- LSTM-based deep learning forecasting
- Edge computing deployment
- Mobile app for store managers

---

## 📝 References

1. G. Jocher, A. Chaurasia, and J. Qiu, "YOLOv8 Documentation," Ultralytics, 2023.
2. G. Bradski, "The OpenCV Library," Dr. Dobb's Journal, 2000.
3. F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," JMLR, 2011.
4. Streamlit Inc., "Streamlit Documentation," 2023.

---

## 👩‍💻 Author

**Sadhvi Singh**
