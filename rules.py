
NEUTRALS = {"أسود", "أبيض", "رمادي فاتح", "رمادي غامق", "بيج", "كحلي"}

MATCHES = {
    "أسود": ["أبيض", "رمادي فاتح", "أحمر", "بيج", "كحلي"],
    "أبيض": ["أسود", "أزرق", "كحلي", "بيج", "أخضر", "زهري"],
    "رمادي فاتح": ["أزرق", "أبيض", "أسود", "كحلي", "زهري"],
    "رمادي غامق": ["أبيض", "أزرق", "زهري", "أحمر"],
    "أزرق": ["رمادي فاتح", "بيج", "أبيض", "بني"],
    "كحلي": ["بيج", "أبيض", "رمادي فاتح", "بني"],
    "أخضر": ["بيج", "أبيض", "بني", "أسود"],
    "أصفر": ["كحلي", "رمادي غامق", "أبيض"],
    "برتقالي": ["كحلي", "بني", "بيج"],
    "بني": ["بيج", "أخضر", "أزرق", "أبيض"],
    "بيج": ["بني", "أبيض", "كحلي", "أخضر", "أسود"],
    "زهري": ["رمادي فاتح", "أبيض", "كحلي"],
    "بنفسجي": ["رمادي فاتح", "أسود", "أبيض"],
    "أحمر": ["أسود", "أبيض", "كحلي"],
    "تركواز": ["أبيض", "بيج", "كحلي"],
}

def _pair_ok(a, b):
    if a in NEUTRALS or b in NEUTRALS:
        return True
    return b in MATCHES.get(a, [])

def evaluate(top, bottom, shoes=None):
    
    result = {
        "top": top, "bottom": bottom, "shoes": shoes,
        "status": None, "suggestion": None, "shoes_ok": None,
    }
    if top and bottom:
        if top == bottom:
            result["status"] = "same_color"
            result["suggestion"] = MATCHES.get(top, ["أبيض"])[0]
        elif _pair_ok(top, bottom):
            result["status"] = "match"
        else:
            result["status"] = "mismatch"
            result["suggestion"] = MATCHES.get(top, ["أبيض"])[0]
    if shoes:
        result["shoes_ok"] = _pair_ok(shoes, bottom or "") or _pair_ok(shoes, top or "")
    return result
