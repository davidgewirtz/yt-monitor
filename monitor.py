import os
import time
import json
import smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==========================================
# CONFIGURATION - Replace with your details
# ==========================================
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

# Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your-sender-address@gmail.com"
RECEIVER_EMAIL = "your-receiver-address@gmail.com"
EMAIL_PASSWORD = "your-16-char-app-password"

# Operational Settings
CHECK_INTERVAL = 3600  # 1 hour in seconds
DATA_FILE = "/app/data/seen_comments.json"
CONSECUTIVE_ERROR_LIMIT = 48  # Alert after 48 hours of failures

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_latest_comments(youtube):
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId=CHANNEL_ID,
            maxResults=50,
            order="time"
        )
        response = request.execute()
        return response.get('items', [])
    except HttpError as e:
        print(f"YouTube API Error: {e}")
        return None

def main():
    print("Starting YouTube comment monitor...")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Load previously seen comments
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            seen_ids = set(json.load(f))
    else:
        seen_ids = set()

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    error_count = 0

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for new comments...")
        items = get_latest_comments(youtube)

        if items is None:
            error_count += 1
            if error_count == CONSECUTIVE_ERROR_LIMIT:
                send_email("⚠️ ALERT: YouTube Monitor Failed", 
                           f"The monitor has failed {CONSECUTIVE_ERROR_LIMIT} times in a row. Check logs.")
        else:
            error_count = 0
            new_comments = []
            
            for item in items:
                comment_id = item['id']
                if comment_id not in seen_ids:
                    new_comments.append(item)
                    seen_ids.add(comment_id)

            if new_comments:
                if not seen_ids: # First run logic
                    print(f"Found {len(new_comments)} comments. Saving history silently...")
                else:
                    print(f"Found {len(new_comments)} new comment(s). Sending email...")
                    body = "\n\n".join([
                        f"From: {c['snippet']['topLevelComment']['snippet']['authorDisplayName']}\n"
                        f"Text: {c['snippet']['topLevelComment']['snippet']['textDisplay']}\n"
                        f"Link: https://www.youtube.com/watch?v={c['snippet']['videoId']}"
                        for c in new_comments
                    ])
                    send_email("New YouTube Comment!", body)

                # Save updated IDs
                with open(DATA_FILE, 'w') as f:
                    json.dump(list(seen_ids), f)
            else:
                print("No new comments found.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
