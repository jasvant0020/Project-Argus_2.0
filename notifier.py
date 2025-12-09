import time
import requests
import threading

BOT_TOKEN = "place_your_Bot_Token_here"
CHAT_ID = "place_your_Chat_Id_here"

DETECTION_COOLDOWN = 5  # seconds
last_detection_times = {}

# Public function used in main.py
def send_telegram_notification(name):
    thread = threading.Thread(target=_send_notification, args=(name,))
    thread.start()

# Internal function doing the actual sending (runs in background thread)
def _send_notification(name):
    now = time.time()
    last_time = last_detection_times.get(name, 0)

    if now - last_time < DETECTION_COOLDOWN:
        return

    message = f"🚨 ALERT: {name} has been detected!"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}

    try:
        response = requests.post(url, data=data, timeout=3)  # prevent blocking webcam
        if response.status_code == 200:
            print(f"✅ Telegram sent for {name}")
            last_detection_times[name] = now
        else:
            print("❌ Telegram error:", response.text)
    except Exception as e:
        print(f"❌ Telegram exception for {name}:", str(e))