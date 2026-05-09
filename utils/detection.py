import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
import os

DEFAULT_MODEL = "yolov8m.pt"
CUSTOM_MODEL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best.pt")

def load_model(use_custom: bool = False) -> YOLO:
    if use_custom and os.path.exists(CUSTOM_MODEL):
        print(f"[Detection] Loading custom model: {CUSTOM_MODEL}")
        return YOLO(CUSTOM_MODEL)
    else:
        print(f"[Detection] Loading default pre-trained model: {DEFAULT_MODEL}")
        return YOLO(DEFAULT_MODEL)
    
def run_detection(image: np.ndarray, model: YOLO, confidence: float = 0.4):
    results = model(image, conf=confidence)[0]

    product_counts = {}
    detections = []

    for box in results.boxes:
        class_id   = int(box.cls[0])
        class_name = model.names[class_id]
        conf_score = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        product_counts[class_name] = product_counts.get(class_name, 0) + 1
        detections.append({
            "class"     : class_name,
            "confidence": round(conf_score, 2),
            "bbox"      : (x1, y1, x2, y2)
        })

    annotated_image, class_colors = draw_boxes(image.copy(), detections)
    return annotated_image, product_counts, detections, class_colors

def draw_boxes(image: np.ndarray, detections: list) -> np.ndarray:
    # Fixed color per class name — same product always same color
    class_colors = {}
    color_palette = [
        (255, 99,  71),   # tomato red
        (50,  205, 50),   # lime green
        (30,  144, 255),  # dodger blue
        (255, 215, 0),    # gold
        (218, 112, 214),  # orchid purple
        (0,   206, 209),  # dark turquoise
        (255, 140, 0),    # dark orange
        (220, 20,  60),   # crimson
        (0,   191, 255),  # deep sky blue
        (127, 255, 0),    # chartreuse
    ]

    color_index = 0

    for det in detections:
        class_name = det["class"]

        # Assign a fixed color per class
        if class_name not in class_colors:
            class_colors[class_name] = color_palette[color_index % len(color_palette)]
            color_index += 1

        color           = class_colors[class_name]
        x1, y1, x2, y2 = det["bbox"]
        label           = f"{det['class']} ({det['confidence']})"

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(image, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)

        cv2.putText(image, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

    return image, class_colors

def preprocess_image(upload_file) -> np.ndarray:
    pil_image = Image.open(upload_file).convert("RGB")
    return np.array(pil_image)