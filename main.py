import cv2
import time
import threading
import logging
from detector import person_present, analyze_outfit
from persona import render
from llm import generate
from tts import speak
from db import log_event
from app import app, set_advice
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[logging.FileHandler("mirror.log", encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger("mirror")

def run_web():
    app.run(host="0.0.0.0", port=config.PORT, threaded=True)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log.error("الكاميرا غير متاحة")
        return

    presence_start = None
    last_advice_time = 0
    log.info("المراية شغالة... بانتظار الزبائن")

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            now = time.time()
            if now - last_advice_time < config.COOLDOWN_SECONDS:
                presence_start = None
                time.sleep(0.2)
                continue

            if person_present(frame):
                if presence_start is None:
                    presence_start = now
                    log.info("تم رصد شخص")
                elif now - presence_start >= config.STABLE_SECONDS:
                    log.info("جارٍ تحليل الإطلالة...")
                    result = analyze_outfit(frame)
                    if result:
                        advice = generate(result) or render(result)
                        if advice:
                            log.info("النصيحة: %s", advice)
                            set_advice(advice)
                            log_event(result, advice)
                            speak(advice)
                    last_advice_time = time.time()
                    presence_start = None
            else:
                presence_start = None

            time.sleep(0.2)
        except Exception as e:
            # أي خطأ غير متوقع لا يوقف المراية
            log.error("خطأ غير متوقع: %s", e)
            time.sleep(1)

if __name__ == "__main__":
    main()
