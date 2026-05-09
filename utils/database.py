import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "inventory.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok = True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS inventory_log(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    detected_count INTEGER NOT NULL,
                    threshold INTEGER DEFAULT 5,
                    status TEXT NOT NULL
                    )
                """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shelf_health_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            availability_score REAL,
            placement_score REAL,
            restock_efficiency REAL,
            shelf_health_score REAL
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

def log_detection(product_counts: dict, thresholds: dict):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for product, count in product_counts.items():
        threshold = thresholds.get(product, 5)

        if count == 0:
            status = "Critical"
        elif count < threshold:
            status = "Low Stock"
        else:
            status = "Normal"

        cursor.execute("""
            INSERT INTO inventory_log (timestamp, product_name, detected_count, threshold, status)
            VALUES (?, ?, ?, ?, ?)
            """, (timestamp, product, count, threshold, status))
        
    conn.commit()
    conn.close()

def log_shelf_health(availability: float, placement: float, restock_eff: float):
    score = round((availability * 0.5) + (placement * 0.3) + (restock_eff * 0.2), 2)
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO shelf_health_log 
        (timestamp, availability_score, placement_score, restock_efficiency, shelf_health_score)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, availability, placement, restock_eff, score))

    conn.commit()
    conn.close()    
    return score

def get_inventory_history(product_name: str = None) -> pd.DataFrame:
    conn = get_connection()

    if product_name:
        df = pd.read_sql_query(
            "SELECT * FROM inventory_log WHERE product_name=? ORDER BY timestamp DESC",
            conn, params=(product_name,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM inventory_log ORDER BY timestamp DESC",
            conn
        )    
    conn.close()
    return df

def get_shelf_health_history() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM shelf_health_log ORDER BY timestamp DESC",
        conn
    )
    conn.close()
    return df

def get_product_list() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT product_name FROM inventory_log")
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return products