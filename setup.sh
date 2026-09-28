#!/bin/bash
set -e
echo "== تحديث النظام =="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git alsa-utils

echo "== بيئة بايثون =="
python3 -m venv ~/mirror-env
source ~/mirror-env/bin/activate
pip install -r requirements.txt

echo "== تثبيت Piper =="
mkdir -p ~/piper && cd ~/piper
wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
tar -xzf piper_arm64.tar.gz
mv piper/* . 2>/dev/null || true

echo "== تنزيل الصوت العربي =="
wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx
wget -q https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ar/ar_JO/kareem/medium/ar_JO-kareem-medium.onnx.json

echo "== تنزيل نموذج YOLO =="
python3 -c "from ultralytics import YOLO; YOLO('yolov8n-seg.pt')"

echo "== تم! شغّل المشروع بـ: source ~/mirror-env/bin/activate && python3 main.py =="
