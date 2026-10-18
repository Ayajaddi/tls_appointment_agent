import os
import time
import requests
from playwright.sync_api import sync_playwright

# جلب البيانات من متغيرات البيئة (Railway Variables)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TLS_EMAIL = os.getenv("TLS_EMAIL")
TLS_PASSWORD = os.getenv("TLS_PASSWORD")

# رابط صفحة تسجيل الدخول لمركز TLScontact تونس العاصمة
TLS_TUNIS_URL = "https://visas-fr.tlscontact.com/visa/tn/tnTUN2fr/home"
CHECK_INTERVAL = 120 # الفحص كل دقيقتين تجنباً لحظر الحساب

def send_telegram_notification(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ خطأ: TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID غير مضبوطين.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"خطأ أثناء الاتصال بتليجرام: {e}")

def check_appointments():
    print("🚀 بدء تشغيل بوت المراقبة الخاص بمركز TLScontact تونس...")
    send_telegram_notification("🟢 <b>البوت يعمل الآن!</b> جاري مراقبة مواعيد TLScontact (تونس العاصمة) مجاناً على مدار الساعة.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        while True:
            try:
                # 1. الذهاب لصفحة تونس العاصمة
                page.goto(TLS_TUNIS_URL, timeout=60000)
                time.sleep(3)

                # 2. إدخال الإيميل وكلمة السر عند ظهور خيارات الدخول
                if page.is_visible("input[type='email']"):
                    page.fill("input[type='email']", TLS_EMAIL)
                    page.fill("input[type='password']", TLS_PASSWORD)
                    page.click("button[type='submit']")
                    time.sleep(5)

                content = page.content()
                
                # 3. فحص توفر المواعيد في تونس
                if "Available" in content or "متاح" in content or "RDV" in content or "appointment" in content.lower():
                    msg = "🚨 <b>عاجل: تم إيجاد موعد متاح الآن في TLScontact تونس!</b>\n\nادخل فوراً للحجز: " + TLS_TUNIS_URL
                    print(msg)
                    send_telegram_notification(msg)
                    time.sleep(600) # الانتظار 10 دقائق بعد التنبيه
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] مركز تونس: لا توجد مواعيد متاحة حالياً. جاري الفحص المستمر...")

            except Exception as e:
                print(f"حدث خطأ أثناء الفحص: {e}")

            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_appointments()
