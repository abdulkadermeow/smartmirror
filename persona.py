import json
import os
import random
from collections import deque

PERSONA_PATH = os.path.join(os.path.dirname(__file__), "persona.json")
_cache = {"data": None, "mtime": 0}
_recent = {}            
RECENT_MEMORY = 3     

def load_persona():
    mtime = os.path.getmtime(PERSONA_PATH)
    if _cache["data"] is None or mtime != _cache["mtime"]:
        with open(PERSONA_PATH, encoding="utf-8") as f:
            _cache["data"] = json.load(f)
        _cache["mtime"] = mtime
    return _cache["data"]

def _pick(status_key, templates):
   
    if isinstance(templates, str):
        templates = [templates]
    used = _recent.setdefault(status_key, deque(maxlen=RECENT_MEMORY))
    available = [t for t in templates if t not in used]
    if not available:
        available = templates
    choice = random.choice(available)
    used.append(choice)
    return choice

def render(result):
    
    persona = load_persona()
    t = persona["templates"]
    top, bottom, shoes = result["top"], result["bottom"], result["shoes"]
    status, suggestion = result["status"], result["suggestion"]

    if top is None and bottom is None:
        return None
    if top is None:
        return _pick("no_top", t["no_top"]).format(bottom=bottom)
    if bottom is None:
        return _pick("no_bottom", t["no_bottom"]).format(top=top)

    if status == "same_color":
        text = _pick("same_color", t["same_color"]).format(top=top, suggestion=suggestion)
    elif status == "match":
        text = _pick("match", t["match"]).format(top=top, bottom=bottom)
    else:
        text = _pick("mismatch", t["mismatch"]).format(top=top, bottom=bottom, suggestion=suggestion)

    if shoes:
        key = "shoes_ok" if result["shoes_ok"] else "shoes_bad"
        text += "، " + _pick(key, t[key]).format(shoes=shoes)
    return text
