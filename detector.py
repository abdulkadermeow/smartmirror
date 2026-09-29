import cv2
import os
import urllib.request
import numpy as np
from ultralytics import YOLO
from colors import dominant_color_name
from rules import evaluate

# موديل كشف الشخص وفصله عن الخلفية (بينزّل تلقائياً أول مرة)
person_model = YOLO("yolov8n-seg.pt")

# موديل كشف قطع اللبس (لبس، حذاء، شنطة، إكسسوار) — بينزّل مرة وحدة من Hugging Face
CLOTH_URL = "https://huggingface.co/kesimeg/yolov8n-clothing-detection/resolve/main/best.pt"
CLOTH_PATH = os.path.join(os.path.dirname(__file__), "clothing.pt")
cloth_model = None

def _load_cloth_model():
    global cloth_model
    if cloth_model is not None:
        return cloth_model
    try:
        if not os.path.exists(CLOTH_PATH):
            print("بتنزّل موديل كشف الملابس (مرة وحدة بس)...")
            urllib.request.urlretrieve(CLOTH_URL, CLOTH_PATH)
        cloth_model = YOLO(CLOTH_PATH)
        print("موديل الملابس جاهز")
    except Exception as e:
        print("موديل الملابس ما اشتغل، برجع للتقسيم التقديري:", e)
        cloth_model = None
    return cloth_model

def get_person(frame):
    results = person_model(frame, verbose=False, imgsz=320)
    r = results[0]
    if r.masks is None:
        return None, None
    for i, box in enumerate(r.boxes):
        if person_model.names[int(box.cls)] == "person" and float(box.conf) > 0.5:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            mask = r.masks.data[i].cpu().numpy()
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
            mask = (mask > 0.5).astype(np.uint8) * 255
            return xyxy, mask
    return None, None

def person_present(frame):
    xyxy, _ = get_person(frame)
    return xyxy is not None

def _color_in_box(frame, mask, box):
    x1, y1, x2, y2 = box
    region = frame[y1:y2, x1:x2]
    region_mask = mask[y1:y2, x1:x2]
    return dominant_color_name(region, region_mask)

def _detect_clothes(frame, mask, person_box):
    """كشف القطع الفعلية: يرجّع ألوان top/bottom/shoes أو None إذا فشل"""
    model = _load_cloth_model()
    if model is None:
        return None
    px1, py1, px2, py2 = person_box
    crop = frame[py1:py2, px1:px2]
    if crop.size == 0:
        return None
    results = model(crop, verbose=False, imgsz=320)
    person_h = py2 - py1
    colors = {"top": None, "bottom": None, "shoes": None}
    found = False
    for box in results[0].boxes:
        name = model.names[int(box.cls)].lower()
        bx1, by1, bx2, by2 = box.xyxy[0].cpu().numpy().astype(int)
        # تحويل إحداثيات القص لإحداثيات الصورة الكاملة
        full_box = (px1 + bx1, py1 + by1, px1 + bx2, py1 + by2)
        rel_center_y = ((by1 + by2) / 2) / max(person_h, 1)
        if "shoe" in name:
            colors["shoes"] = colors["shoes"] or _color_in_box(frame, mask, full_box)
            found = True
        elif "cloth" in name:
            # القطعة الفوقانية أو التحتانية حسب موقعها من جسم الشخص
            color = _color_in_box(frame, mask, full_box)
            if rel_center_y < 0.5:
                colors["top"] = colors["top"] or color
            else:
                colors["bottom"] = colors["bottom"] or color
            found = True
    return colors if found else None

def _detect_by_zones(frame, mask, person_box):
    """الخطة البديلة: التقسيم النسبي للجسم (الطريقة القديمة)"""
    x1, y1, x2, y2 = person_box
    h = y2 - y1
    zones = {"top": (0.15, 0.52), "bottom": (0.52, 0.88), "shoes": (0.88, 1.00)}
    colors = {}
    for zone, (a, b) in zones.items():
        ys, ye = y1 + int(h * a), y1 + int(h * b)
        region = frame[ys:ye, x1:x2]
        region_mask = mask[ys:ye, x1:x2]
        colors[zone] = dominant_color_name(region, region_mask)
    return colors

def analyze_outfit(frame):
    """تحليل الإطلالة: موديل الملابس أولاً، وعند فشله التقسيم التقديري"""
    person_box, mask = get_person(frame)
    if person_box is None:
        return None
    if person_box[3] - person_box[1] < 80:
        return None
    colors = _detect_clothes(frame, mask, person_box)
    if colors is None:
        colors = _detect_by_zones(frame, mask, person_box)
    if colors["top"] is None and colors["bottom"] is None:
        return None
    return evaluate(colors["top"], colors["bottom"], colors["shoes"])
