import time
import requests
from datetime import datetime
import pytz
import google.generativeai as genai

# ==========================================
# المفاتيح والبيانات الخاصّة بك
# ==========================================
GEMINI_API_KEY = "AQ.Ab8RN6JYD2vDw3ytFgeTRzCHPzd9-bWnkFnHbqQj7LGGLhS29Q"
TELEGRAM_BOT_TOKEN = "8913585593:AAE2qayGXug57XhnJUuFjJKAB4sBkDazPuM"
TELEGRAM_CHAT_ID = 8060030812

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
أنت أيجنت ذكاء اصطناعي متخصص في تحليل أخبار وسوق العملات الرقمية. لست مستشاراً مالياً، ومهمتك هي تحليل الأخبار المجلوبة بدقة وحيادية.

العملات المستهدفة حصراً:
1. Worldcoin (WLD)
2. Ripple (XRP)
3. Cardano (ADA)
4. Hedera (HBAR)

قواعد التحليل:
- قم بقراءة الأخبار المتعلقة بالعملات الأربع أعلاه فقط، وتجاهل أي عملة أخرى.
- ترفع من قيمة الأخبار الصادرة من المصادر الرسمية أو الهيئات التنظيمية، وتقلل من قيمة الشائعات والتغريدات التسويقية.

شكل التقرير المطلوب إرساله في الشات:
🟢 تأثير الخبر: [إيجابي / سلبي / محايد] — التقييم: [مثلاً: 8/10]
* 🪙 العملة: [اسم العملة والرمز]
* 📝 ملخص الخبر: [ملخص مباشر وسريع في سطرين]
* 💡 سبب التأثير: [شرح مختصر لسبب إيجابية أو سلبية الخبر]
* ⏳ المدى الزمني: [تأثير لحظي/سريع أم للمدى الطويل؟]
"""

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=SYSTEM_PROMPT
)

def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

def get_sleep_interval():
    kuwait_tz = pytz.timezone('Asia/Kuwait')
    current_hour = datetime.now(kuwait_tz).hour
    if current_hour >= 15 or current_hour < 5:
        return 1800  # 30 دقيقة
    else:
        return 7200  # ساعتين

print(f"✅ تم التشغيل على السيرفر الدائم! Chat ID: {TELEGRAM_CHAT_ID}")
send_telegram_message(TELEGRAM_CHAT_ID, "🚀 تم نقل أيجنت الكريبتو للسيرفر الدائم (Render) بنجاح!")

while True:
    try:
        kuwait_tz = pytz.timezone('Asia/Kuwait')
        now_str = datetime.now(kuwait_tz).strftime('%Y-%m-%d %I:%M %p')
        print(f"\n[{now_str}] جاري فحص السوق...")
        
        prompt = "هل هناك أي أخبار حديثة أو هامة خلال الساعات الماضية لعملات WLD, XRP, ADA, HBAR؟ إذا وجد خبر يرجى تحليله بالصيغة المحددة."
        response = model.generate_content(prompt)
        
        if response.text:
            send_telegram_message(TELEGRAM_CHAT_ID, response.text)
            print("🟢 تم إرسال التقرير لتليجرام!")
            
    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
        
    sleep_time = get_sleep_interval()
    print(f"😴 الفحص القادم بعد {sleep_time // 60} دقيقة...")
    time.sleep(sleep_time)
