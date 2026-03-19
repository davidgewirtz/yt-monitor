# 📺 YouTube Comment Monitor (Self-Hosted)

A lightweight Python script designed to run in a Docker container. It monitors your YouTube channel for new comments and sends email alerts via Gmail SMTP.

## ✨ Features
* **Automated Monitoring:** Checks for new comments every hour.
* **Persistent Memory:** Uses a local JSON file to prevent duplicate alerts.
* **Failure Detection:** Sends an alert email if the API connection fails repeatedly.
* **Docker Optimized:** Designed for home servers (Mac Mini, Synology, Raspberry Pi).

---

## 🚀 Setup Instructions

### 1. Prerequisites
* **Google Cloud Console:** Enable the YouTube Data API v3 and generate an API Key.
* **Gmail:** Enable 2FA and generate a 16-character App Password.
* **Docker/Portainer:** Installed on your hosting machine.

### 2. Configuration
Edit monitor.py and replace these placeholders:
* YOUTUBE_API_KEY: Your Google API Key.
* CHANNEL_ID: Your YouTube Channel ID (starts with UC...).
* SENDER_EMAIL: Your Gmail address.
* RECEIVER_EMAIL: Where to send alerts.
* EMAIL_PASSWORD: Your 16-character Gmail App Password.

### 3. Build & Deploy
In your terminal, navigate to the project folder and run:
docker build -t yt-comment-monitor .

### 4. Portainer Configuration
* Name: my-yt-monitor
* Image: yt-comment-monitor
* Always pull image: OFF
* Volumes (Bind):
  * Container: /app/data
  * Host: /opt/yt-monitor/data
* Restart Policy: Unless stopped

---

## 🛠 Maintenance

### Checking activity
Check the Logs tab in Portainer. You should see:
- Checking for new comments...
- No new comments found.

### Updating the script
If you modify monitor.py, rebuild and restart with:
docker build -t yt-comment-monitor . && docker restart my-yt-monitor

## 📝 License
MIT License
