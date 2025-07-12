import os, shutil
from datetime import datetime

RAM_LOG_PATH = "/mnt/ramlogs/today.log"
DISK_LOG_DIR = os.path.expanduser("~/wifi_logger/logs")
os.makedirs(DISK_LOG_DIR, exist_ok=True)

print(f"[DEBUG] Checking for {RAM_LOG_PATH}")

if os.path.exists(RAM_LOG_PATH):
    today = datetime.now().strftime("%Y-%m-%d")
    final_path = os.path.join(DISK_LOG_DIR, f"{today}.log")
    print(f"[DEBUG] Flushing to {final_path}")
    shutil.copy(RAM_LOG_PATH, final_path)
else:
    print("[DEBUG] RAM log not found. Nothing to flush.")
