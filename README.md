# Raspberry Pi WiFi Packet Logger

This project provides a small network logger designed for Raspberry Pi or other Linux systems. It captures outbound IP traffic, resolves the destination to a hostname and geographic location, and stores the results. Logs are buffered in RAM to reduce SD card wear and periodically flushed to disk.

## Features

- **Packet capture** via `scapy` for all outbound IP packets
- **DNS and Geo-IP lookups** using `socket` and the ipinfo.io API
- **In-memory caching** for DNS and location results to minimise API calls
- **RAM log** located at `/mnt/ramlogs/today.log`
- **Daily disk archive** under `~/wifi_logger/logs/YYYY-MM-DD.log`
- **Systemd service** example for unattended operation

## Repository Layout

```
flush_to_disk.py   # Script to copy the RAM log to disk
live_logger.py     # Main traffic logger
read.md            # Previous README content
```

## Requirements

- Python 3
- `scapy`, `requests`, and `python-dotenv`
- `tcpdump` and `nmap` (for packet capture)

Install the dependencies:

```bash
sudo apt update
sudo apt install python3-pip tcpdump nmap -y
pip3 install scapy requests python-dotenv
```

If you use a virtual environment:

```bash
python3 -m venv ~/scapy-env
source ~/scapy-env/bin/activate
pip install scapy requests python-dotenv
```

## Configuration

1. Obtain a token from [ipinfo.io](https://ipinfo.io/).
2. Create `~/.env` containing your API token:
   ```bash
echo 'IPINFO_TOKEN=your_token_here' > ~/.env
   ```
3. Set up the RAM directory used for temporary logs:
   ```bash
sudo mkdir -p /mnt/ramlogs
sudo mount -t tmpfs -o size=50M tmpfs /mnt/ramlogs
   ```
   To keep the mount across reboots, add the following to `/etc/fstab`:
   ```
tmpfs /mnt/ramlogs tmpfs defaults,size=50M 0 0
   ```

## Running

Run the logger manually:

```bash
python3 live_logger.py
```

To persist the log to disk, run:

```bash
python3 flush_to_disk.py
```

### Systemd Service (optional)

Create `/etc/systemd/system/live-logger.service`:

```
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
```

Enable and start the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable live-logger
sudo systemctl start live-logger
```

### Flushing Logs Automatically

A daily cron job can call `flush_to_disk.py` just before midnight:

```cron
59 23 * * * /usr/bin/python3 /home/user/wifi_logger/flush_to_disk.py
```

## Notes

- Internal traffic (`192.x.x.x` to `192.x.x.x`) is ignored.
- Cached geolocation data is stored in `ip_location_cache.json`.
- If the machine reboots before the RAM log is flushed, the log is lost.
- Some IPs may not resolve to domains and will be labelled `unknown`.

## License

MIT License

