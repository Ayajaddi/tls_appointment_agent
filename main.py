import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # Check every 60 seconds

def send_telegram_notification(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Warning: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variable not set.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error communicating with Telegram: {e}")

def check_appointments():
    print("🚀 Starting TLScontact free monitoring agent...")
    send_telegram_notification("🟢 <b>البوت يعمل الآن!</b> يتم فحص مواعيد TLScontact مجاناً على مدار الساعة.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        while True:
            try:
                page.goto("https://visas-fr.tlscontact.com/", timeout=60000)
                content = page.content()
                
                if "Available" in content or "متاح" in content or "RDV" in content:
                    msg = "🚨 <b>عاجل: تم إيجاد موعد متاح الآن على TLScontact!</b>\n\nادخل فوراً للحجز: https://visas-fr.tlscontact.com/"
                    print(msg)
                    send_telegram_notification(msg)
                    time.sleep(300)
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No available appointments currently. Retrying...")

            except Exception as e:
                print(f"Error during check: {e}")

            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_appointments()
