import subprocess
import os
import platform

PIPER_BIN = os.path.expanduser("~/piper/piper")
PIPER_MODEL = os.path.expanduser("~/piper/ar_JO-kareem-medium.onnx")
OUT_WAV = "/tmp/advice.wav"

def _speak_windows(text):
    """نطق على ويندوز عبر أصوات النظام (SAPI)"""
    import pyttsx3
    engine = pyttsx3.init()
    # محاولة اختيار صوت عربي إذا كان مثبتاً على الجهاز
    for voice in engine.getProperty("voices"):
        if "arabic" in voice.name.lower() or "ar" in voice.id.lower():
            engine.setProperty("voice", voice.id)
            break
    engine.setProperty("rate", 160)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def _speak_linux(text):
    """نطق على لينكس/راسبيري عبر Piper"""
    with open("/tmp/advice.txt", "w", encoding="utf-8") as f:
        f.write(text)
    subprocess.run(
        f"cat /tmp/advice.txt | {PIPER_BIN} --model {PIPER_MODEL} --output_file {OUT_WAV}",
        shell=True, check=True,
    )
    subprocess.run(["aplay", OUT_WAV], check=True)

def speak(text):
    """نطق النصيحة حسب نظام التشغيل، وأي فشل لا يوقف المشروع"""
    try:
        if platform.system() == "Windows":
            _speak_windows(text)
        else:
            _speak_linux(text)
    except Exception as e:
        print("مشكلة بالصوت:", e)
