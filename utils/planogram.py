import json
import os

PLANOGRAM_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    "data", "planogram","planogram.json"
)

def load_planogram() -> dict:
    if not os.path.exists(PLANOGRAM_PATH):
        return {}
    with open(PLANOGRAM_PATH, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)
    
def save_planogram(planogram: dict):
    os.makedirs(os.path.dirname(PLANOGRAM_PATH), exist_ok=True)
    with open(PLANOGRAM_PATH, "w") as f:
        json.dump(planogram, f, indent=4)

def validate_planogram(detected_products: dict, planogram: dict) -> dict:
    if not planogram:
        return {
            "matched": [],
            "missing": [],
            "extra": list(detected_products.keys()),
            "placement_score": 1.0
        }
    matched = []
    missing = []
    extra = []

    for product in planogram:
        if product in detected_products:
            matched.append(product)
        else:
            missing.append(product)

    for product in detected_products:
        if product not in planogram:
            extra.append(product)

    total_expected = len(planogram)
    placement_score = len(matched) / total_expected if total_expected > 0 else 1.0

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "placement_score": round(placement_score, 2)  
    }

def compute_availability_score(detected_products: dict, thresholds: dict) -> float:
    if not detected_products:
        return 0.0
    
    above_threshold = sum(
        1 for p, c in detected_products.items() 
        if c >= thresholds.get(p, 5)
    )
    return round(above_threshold / len(detected_products), 2) 

def create_default_planogram(product_list: list, default_count: int = 5):
    planogram = {p: default_count for p in product_list}
    save_planogram(planogram)
    return planogram