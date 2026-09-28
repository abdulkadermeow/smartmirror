import cv2
import numpy as np
from ultralytics import YOLO
from colors import dominant_color_name
from rules import evaluate

model = YOLO("yolov8n-seg.pt")

def get_person(frame):
    results = model(frame, verbose=False, imgsz=320)
    r = results[0]
    if r.masks is None:
        return None, None
    for i, box in enumerate(r.boxes):
        if model.names[int(box.cls)] == "person" and float(box.conf) > 0.5:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            mask = r.masks.data[i].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            mask = (mask > 0.5).astype(np.uint8) * 255
            return xyxy, mask
    return None, None

def person_present(frame):
    xyxy, _ = get_person(frame)
    return xyxy is not None

def analyze_outfit(frame):
    """يرجّع نتيجة خام: ألوان القطع + حالة التناسق (بدون صياغة)"""
    xyxy, mask = get_person(frame)
    if xyxy is None:
        return None
    x1, y1, x2, y2 = xyxy
    h = y2 - y1
    if h < 80:
        return None
    zones = {"top": (0.15, 0.52), "bottom": (0.52, 0.88), "shoes": (0.88, 1.00)}
    colors = {}
    for zone, (a, b) in zones.items():
        ys, ye = y1 + int(h * a), y1 + int(h * b)
        region = frame[ys:ye, x1:x2]
        region_mask = mask[ys:ye, x1:x2]
        colors[zone] = dominant_color_name(region, region_mask)
    if colors["top"] is None and colors["bottom"] is None:
        return None
    return evaluate(colors["top"], colors["bottom"], colors["shoes"])
