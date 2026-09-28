import json
import os
import shutil
from flask import Flask, render_template, jsonify, request, redirect
from persona import load_persona, PERSONA_PATH
from db import get_stats
import config

app = Flask(__name__)
current_advice = {"text": "", "id": 0}

def set_advice(text):
    current_advice["text"] = text
    current_advice["id"] += 1

@app.route("/")
def index():
    return render_template("index.html", display_ms=config.ADVICE_DISPLAY_MS)

@app.route("/advice")
def advice():
    return jsonify(current_advice)

@app.route("/persona")
def persona_api():
    p = load_persona()
    return jsonify({"brand_name": p["brand_name"], "theme": p["theme"]})

def _list_presets():
    folder = os.path.join(os.path.dirname(__file__), "personas")
    return [f[:-5] for f in os.listdir(folder) if f.endswith(".json")]

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") != config.ADMIN_PASSWORD:
            return render_template("admin.html", persona=load_persona(),
                                   presets=_list_presets(), error="كلمة السر غلط")
        action = request.form.get("action")

        if action == "apply_preset":
            preset = request.form.get("preset")
            src = os.path.join(os.path.dirname(__file__), "personas", preset + ".json")
            if os.path.exists(src):
                shutil.copy(src, PERSONA_PATH)
            return redirect("/admin?saved=1")

        persona = load_persona()
        persona["brand_name"] = request.form.get("brand_name", persona["brand_name"])
        persona["tone"] = request.form.get("tone", persona["tone"])
        persona["use_llm"] = request.form.get("use_llm") == "on"
        persona["theme"]["accent"] = request.form.get("accent", persona["theme"]["accent"])
        for key in persona["templates"]:
            templates = persona["templates"][key]
            if isinstance(templates, list):
                for i in range(len(templates)):
                    val = request.form.get(f"tpl_{key}_{i}")
                    if val:
                        persona["templates"][key][i] = val
            else:
                val = request.form.get(f"tpl_{key}")
                if val:
                    persona["templates"][key] = val
        with open(PERSONA_PATH, "w", encoding="utf-8") as f:
            json.dump(persona, f, ensure_ascii=False, indent=2)
        return redirect("/admin?saved=1")

    stats = get_stats()
    return render_template("admin.html", persona=load_persona(),
                           presets=_list_presets(), stats=stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, threaded=True)
