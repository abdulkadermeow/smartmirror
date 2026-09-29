import cv2
import numpy as np
from sklearn.cluster import KMeans

def is_skin(rgb):
   
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])

    if r > 60 and r > g > b and (r - b) > 15 and abs(r - g) > 10:
        return True
    return False

def name_from_hsv(h, s, v):
   
    if v < 45:
        return "أسود"
    if s < 40:
        if v > 200:
            return "أبيض"
        if v > 110:
            return "رمادي فاتح"
        return "رمادي غامق"
  
    if h < 8 or h >= 170:
        return "أحمر"
    if h < 15:
        return "برتقالي"
    if h < 25:
        return "بني" if v < 150 else "برتقالي"
    if h < 35:
        return "أصفر"
    if h < 45:
        return "بيج" if s < 110 else "أصفر"
    if h < 85:
        return "أخضر"
    if h < 100:
        return "تركواز"
    if h < 130:
        return "أزرق" if v > 90 else "كحلي"
    if h < 155:
        return "بنفسجي"
    return "زهري"

def dominant_color_name(region_bgr, mask=None):
   
    if mask is not None:
        pixels = region_bgr[mask > 0]
    else:
        pixels = region_bgr.reshape(-1, 3)
    if len(pixels) < 50:
        return None

    
    rgb_pixels = pixels[:, ::-1]
    keep = np.array([not is_skin(p) for p in rgb_pixels[::5]])  
    sampled = pixels[::5][keep]
    if len(sampled) < 30:
        sampled = pixels[::5]

    
    k = min(3, len(sampled))
    km = KMeans(n_clusters=k, n_init=3).fit(sampled.astype(float))
    counts = np.bincount(km.labels_)
    dom_bgr = km.cluster_centers_[counts.argmax()].astype(np.uint8)

    
    hsv = cv2.cvtColor(np.uint8([[dom_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    return name_from_hsv(int(hsv[0]), int(hsv[1]), int(hsv[2]))
