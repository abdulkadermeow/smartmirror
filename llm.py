import json
import urllib.request
from persona import load_persona

OLLAMA_URL = "http://localhost:11434/api/generate"
TIMEOUT = 20  # ثانية

PROMPT_TEMPLATE = """أنت مراية ذكية في {brand}. نبرتك {tone_desc}.
شخص واقف قدامك وإطلالته: القطعة الفوقانية {top}، القطعة التحتانية {bottom}، الحذاء {shoes}.
تقييم التناسق: {status_desc}. الاقتراح البديل: {suggestion}.
اكتب نصيحة واحدة قصيرة باللهجة العامية العربية (جملة أو جملتين كحد أقصى) بأسلوب {tone_desc}.
لا تكرر نفس الردود السابقة. رد بنص النصيحة فقط بدون أي مقدمات أو شرح."""

TONES = {
    "formal": "رسمية وراقية",
    "friendly": "ودودة ودافئة",
    "playful": "خفيفة دم ومرحة",
}

STATUS_DESC = {
    "match": "الألوان متناسقة وممتازة، امدح الإطلالة",
    "same_color": "الإطلالة كلها بلون واحد، امدح الجرأة واقترح كسر اللون باللون البديل",
    "mismatch": "الألوان غير متناسقة، امدح القطعة الفوقانية واقترح اللون البديل للقطعة التحتانية بلطف",
}

def generate(result):
    """
    توليد نصيحة عبر مودل محلي. بيرجّع None إذا المودل مش شغال
    (ساعتها main.py بيرجع للقوالب تلقائياً).
    """
    persona = load_persona()
    if not persona.get("use_llm"):
        return None

    top = result.get("top") or "غير واضحة"
    bottom = result.get("bottom") or "غير واضحة"
    shoes = result.get("shoes") or "غير واضح"
    status = STATUS_DESC.get(result.get("status"), "قيّم الإطلالة بشكل عام")
    tone = TONES.get(persona.get("tone"), "ودودة")

    prompt = PROMPT_TEMPLATE.format(
        brand=persona.get("brand_name", "المحل"),
        tone_desc=tone, top=top, bottom=bottom, shoes=shoes,
        status_desc=status, suggestion=result.get("suggestion") or "أبيض",
    )

    payload = json.dumps({
        "model": persona.get("llm_model", "qwen2.5:3b-instruct-q4_K_M"),
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.9, "num_predict": 80},
    }).encode("utf-8")

    try:
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data.get("response", "").strip()
            return text if len(text) > 5 else None
    except Exception as e:
        print("المودل المحلي مش متاح، برجع للقوالب:", e)
        return None
