from scapy.all import sniff, IP
import socket
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import atexit
import shutil
import json

# === Load environment variables ===
load_dotenv(dotenv_path=os.path.expanduser("~/.env"))
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")

# === Paths ===
RAM_LOG_PATH = "/mnt/ramlogs/today.log"
DISK_LOG_DIR = os.path.expanduser("~/wifi_logger/logs")
GEO_CACHE_FILE = os.path.expanduser("~/wifi_logger/ip_location_cache.json")
os.makedirs(DISK_LOG_DIR, exist_ok=True)

# === In-memory caches ===
GEO_CACHE = {}
DNS_CACHE = {}

# === Load geolocation cache from file ===
def load_geo_cache():
    if os.path.exists(GEO_CACHE_FILE):
        try:
            with open(GEO_CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

# === Save geolocation cache to file ===
def save_geo_cache():
    try:
        with open(GEO_CACHE_FILE, "w") as f:
            json.dump(GEO_CACHE, f)
    except Exception as e:
        print(f"[Error] Failed to save GEO_CACHE: {e}")

# Load existing geo cache at startup
GEO_CACHE = load_geo_cache()

# === Resolve domain name from IP ===
def get_domain(ip):
    if ip in DNS_CACHE:
        return DNS_CACHE[ip]
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except Exception:
        domain = "unknown"
    DNS_CACHE[ip] = domain
    return domain

# === Get geolocation, with persistent cache ===
def get_location(ip):
    if ip in GEO_CACHE:
        return GEO_CACHE[ip]
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}", timeout=2)
        data = r.json()
        loc = f"{data.get('city', 'Unknown')}, {data.get('region', '')}, {data.get('country', '')}"
        GEO_CACHE[ip] = loc
        save_geo_cache()
    except Exception:
        loc = "Unknown"
    return loc

# === Flush RAM log to permanent disk ===
def flush_to_disk():
    if not os.path.exists(RAM_LOG_PATH):
        return
    today = datetime.now().strftime("%Y-%m-%d")
    final_path = os.path.join(DISK_LOG_DIR, f"{today}.log")
    try:
        shutil.copy(RAM_LOG_PATH, final_path)
        print(f"[Flush] Copied {RAM_LOG_PATH} → {final_path}")
    except Exception as e:
        print(f"[Error] Failed to flush log: {e}")

# Register flush on shutdown
atexit.register(flush_to_disk)

# === Handle each packet ===
def process_packet(packet):
    if IP in packet:
        ip_layer = packet[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst

        # Skip internal traffic
        if src_ip.startswith("192.") and dst_ip.startswith("192."):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        domain = get_domain(dst_ip)
        location = get_location(dst_ip)

        log_line = f"[{timestamp}] {src_ip} → {dst_ip} ({domain}) | {location}"
        print(log_line)

        try:
            with open(RAM_LOG_PATH, "a") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"[Error] Failed to write to RAM log: {e}")

# === Start sniffing ===
print("[Start] Sniffing traffic...")
sniff(filter="ip", prn=process_packet, store=0)
