# 📡 Raspberry Pi Network Traffic Logger

A lightweight traffic logger for Raspberry Pi that captures outbound traffic, resolves destination IPs to domain names and geolocations, and logs results to RAM (to minimize SD card wear). Logs are flushed to disk daily.

---

## ✨ Features

- 🔍 Captures all outbound IP traffic (ignores local/internal)
- 🌐 Resolves destination IPs to domains and physical locations (via ipinfo.io)
- 💾 Buffers logs in RAM (`/mnt/ramlogs/today.log`) to preserve SD card lifespan
- 📁 Flushes daily logs to disk (`~/wifi_logger/logs/YYYY-MM-DD.log`)
- 🧠 Persistent IP geolocation cache in JSON to minimize API calls
- 🔁 Runs 24/7 as a systemd service (auto-restarts and auto-starts on boot)

---

## 📁 Project Structure

wifi_logger/
├── live_logger.py # Main packet logger
├── flush_to_disk.py # Flush RAM log to disk
├── ip_location_cache.json # Geo IP cache (auto-generated)
├── logs/ # Flushed daily log files
├── service_stdout.log # (Optional) systemd stdout log
├── service_stderr.log # (Optional) systemd stderr log
└── .env # Contains IPINFO_TOKEN


---

## ⚙️ Setup

### 1. Install dependencies

```bash
sudo apt update
sudo apt install python3-pip tcpdump nmap -y
pip3 install scapy requests python-dotenv

### 2. (Optional) Set up a virtual environment

python3 -m venv ~/scapy-env
source ~/scapy-env/bin/activate
pip install scapy requests python-dotenv

### 3. Configure API token
echo 'IPINFO_TOKEN=your_token_here' > ~/.env

Create an account at ipinfo.io to get a free token.

### 4. Set up RAM log directory

sudo mkdir -p /mnt/ramlogs
sudo mount -t tmpfs -o size=50M tmpfs /mnt/ramlogs
To make this persist across reboots, add to /etc/fstab:

tmpfs /mnt/ramlogs tmpfs defaults,size=50M 0 0

5. Create systemd service

Create: /etc/systemd/system/live-logger.service


[Unit]
Description=WiFi Live Logger
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/user/wifi_logger/live_logger.py
WorkingDirectory=/home/user/wifi_logger
StandardOutput=null
StandardError=null
Restart=always
User=root
Environment=IPINFO_TOKEN=your_token_here

[Install]
WantedBy=multi-user.target


Then run:
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable live-logger
sudo systemctl start live-logger

🧹 Flushing RAM Logs to Disk
To manually flush logs:
sudo python3 /home/user/wifi_logger/flush_to_disk.py
sudo crontab -e
59 23 * * * /usr/bin/python3 /home/user/wifi_logger/flush_to_disk.py

🧠 Notes
Internal traffic (192.x.x.x → 192.x.x.x) is ignored

IPs are cached after first lookup in ip_location_cache.json

If you reboot before flushing, RAM logs are lost

Domain resolution may fail for some IPs ("unknown")

✅ Future Ideas
 Flush logs hourly or based on file size

 mDNS or nmap-based local device name mapping

 SQLite-based log archive

 Real-time dashboard with filtering

 Alert on suspicious domains or unknown geos

🛡️ License
MIT License — modify and share freely.

---

Let me know if you'd like this README to include screenshots, system diagrams, or a badge (e.g., uptime status).
