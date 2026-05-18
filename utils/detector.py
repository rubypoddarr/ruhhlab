import cv2
import numpy as np
from ultralytics import YOLO
import os

_model = None

SYNONYM_MAP = {
    'automobile': 'car',
    'vehicle': 'car',
    'mobile': 'cell phone',
    'mobile phone': 'cell phone',
    'smartphone': 'cell phone',
    'motorbike': 'motorcycle',
    'couch': 'sofa',
}

def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), '..', 'yolov8n.pt')
        if os.path.exists(model_path):
            _model = YOLO(model_path)
        else:
            _model = YOLO('yolov8n.pt')
    return _model


def normalize_label(label):
    label = label.lower().strip()
    return SYNONYM_MAP.get(label, label)


def detect(image_path, confidence_threshold=0.4):
    model = get_model()
    image = cv2.imread(image_path)
    if image is None:
        return [], None

    h, w = image.shape[:2]
    max_dim = 640
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)))

    results = model(image, verbose=False)[0]

    detected = []
    seen_labels = {}

    for box in results.boxes:
        conf = float(box.conf[0])
        if conf < confidence_threshold:
            continue
        cls_id = int(box.cls[0])
        label = normalize_label(results.names[cls_id])
        if label in seen_labels:
            if conf > seen_labels[label]['confidence']:
                seen_labels[label] = {'label': label, 'confidence': round(conf, 2), 'box': box.xyxy[0].tolist()}
        else:
            seen_labels[label] = {'label': label, 'confidence': round(conf, 2), 'box': box.xyxy[0].tolist()}

    detected = list(seen_labels.values())
    detected.sort(key=lambda x: x['confidence'], reverse=True)

    annotated = annotate_image(image, detected)

    del results
    return detected, annotated


def annotate_image(image, detections):
    annotated = image.copy()
    colors = {
        'person': (0, 255, 200),
        'car': (255, 100, 0),
        'cell phone': (200, 0, 255),
        'default': (0, 200, 255),
    }

    for det in detections:
        box = det['box']
        label = det['label']
        conf = det['confidence']
        color = colors.get(label, colors['default'])

        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

        text = f"{label} {conf:.2f}"
        font_scale = 0.55
        thickness = 1
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
        cv2.putText(annotated, text, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

    del image
    return annotated
