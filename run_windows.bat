@echo off
chcp 65001 >nul
call mirror-env\Scripts\activate.bat
start "" http://localhost:5000
python main.py
pause
