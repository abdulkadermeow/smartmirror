@echo off
chcp 65001 >nul
echo === تجهيز المراية الذكية على ويندوز ===
python -m venv mirror-env
call mirror-env\Scripts\activate.bat
pip install -r requirements.txt
pip install pyttsx3
echo.
echo === خلص التثبيت! للتشغيل نفذ: run_windows.bat ===
pause
