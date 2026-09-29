import subprocess
import os
import platform
import asyncio
import tempfile

PIPER_BIN = os.path.expanduser("~/piper/piper")
PIPER_MODEL = os.path.expanduser("~/piper/ar_JO-kareem-medium.onnx")
OUT_WAV = "/tmp/advice.wav"

# صوت أردني من مايكروسوفت: ذكر ar-JO-TaimNeural / أنثى ar-JO-SanaNeural
JO_VOICE = "ar-JO-TaimNeural"

def _speak_windows(text):
    """نطق على ويندوز بصوت أردني عبر edge-tts، مع رجوع لأصوات النظام عند الفشل"""
    try:
        import edge_tts
        mp3_path = os.path.join(tempfile.gettempdir(), "advice.mp3")
        async def _make():
            tts = edge_tts.Communicate(text, JO_VOICE)
            await tts.save(mp3_path)
        asyncio.run(_make())
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)
        pygame.mixer.quit()
    except Exception as e:
        print("صوت edge-tts ما اشتغل، برجع لأصوات ويندوز:", e)
        import pyttsx3
        engine = pyttsx3.init()
        for voice in engine.getProperty("voices"):
            if "arabic" in voice.name.lower() or "ar" in voice.id.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
        engine.stop()

def _speak_linux(text):
    """نطق على لينكس/راسبيري عبر Piper بصوت أردني (ar_JO-kareem)"""
    with open("/tmp/advice.txt", "w", encoding="utf-8") as f:
        f.write(text)
    subprocess.run(
        f"cat /tmp/advice.txt | {PIPER_BIN} --model {PIPER_MODEL} --output_file {OUT_WAV}",
        shell=True, check=True,
    )
    subprocess.run(["aplay", OUT_WAV], check=True)

def speak(text):
    try:
        if platform.system() == "Windows":
            _speak_windows(text)
        else:
            _speak_linux(text)
    except Exception as e:
        print("مشكلة بالصوت:", e)
