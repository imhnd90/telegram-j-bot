import re
import os
import threading
import time
import requests  # 🌟 Essential for sending the free WhatsApp cloud payload
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageEntityTextUrl, MessageEntityUrl

# --- CONFIGURATION ---
API_ID = 35769422  
API_HASH = '9f5fdb40f517efb629843d96ddaa5a71'  

# 🌟 GREEN-API WHATSAPP CREDENTIALS (FILL THESE WITH YOUR DATA)
GREEN_API_ID = '710522728838'            
GREEN_API_TOKEN ='6dbb40f208984ebab3908788583748b822b453ad99bb487da5'    
WHATSAPP_CHAT_ID = '120363430663266458'   

SOURCE_CHANNELS = [
    '@ewdifh',
    '@cd4cd',
    '@teleworksjobs',
    '@wadhefadotcom',
    '@i8mhnd',
    '@jobs4ksa',
    '@hrgksa',
    '@saudijobs24',
    '@jobs2ksa'
]

DESTINATION_CHANNEL = '@sammhnd'  

JOB_KEYWORDS = [
    # --- Breaking News & Regulatory Filters (Arabic & English) ---
    'عاجل', 'رسميا', 'رسمياً', 'وزارة', 'الوزارة', 'الموارد البشرية', 'قرارات', 'قرار', 'توطين', 
    'سعودة', 'هدف', 'صندوق', 'بيان رسمي', 'تعلن', 'يعلن', 'أعلنت', 'اعلت', 'mhrsd', 'hrdf', 'qiwa',
    
    # --- Corporate Entities & Major Giga-Projects ---
    'شركة', 'أرامكو', 'ارامكو', 'stc', 'الاتصالات', 'نيوم', 'neom', 'سابك', 'البحر الأحمر', 
    'روشن', 'المربع الجديد', 'بنك', 'مصرف', 'الراجحي', 'الأهلي', 'طيران', 'الخطوط', 'مستشفى',
    
    # --- General Employment & Vacancy Types ---
    'وظيفة', 'وظايف', 'وظائف', 'شواغر', 'شاغر', 'شاغرة', 'توظيف', 'تدريب', 'فرصة عمل', 'فرص عمل', 
    'مطلوب', 'مطلوبة', 'برنامج', 'حكومي', 'اداري', 'إداري', 'استقبال', 'خدمة عملاء', 'مبيعات',
    'hiring', 'vacancy', 'job', 'jobs', 'internship', 'career', 'careers', 'apply', 'recruitment',

    # --- On-Site Technical, Field & Corporate Roles ---
    'مهندس', 'هندسة', 'محاسب', 'محاسبة', 'قانوني', 'محامي', 'تقنية', 'معلومات', 'برمجة', 'مطور',
    'امن سيبراني', 'ذكاء اصطناعي', 'شبكات', 'سلاسل الإمداد', 'لوجستي', 'مستودع', 'مشتريات',
    'engineer', 'accounting', 'finance', 'logistics', 'procurement', 'developer', 'python'
]

PROMO_KEYWORDS = []

# 🌟 ANTI-DUPLICATE CACHE DICTIONARY
processed_messages_cache = set()
cache_lock = threading.Lock()

client = TelegramClient('render_cloud_session', API_ID, API_HASH)

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", "18")
        self.end_headers()
        self.wfile.write(b"Bot is active 24/7")

    def log_message(self, format, *args):
        return

def run_web_server():
    """Runs a tiny web server in the background to satisfy Render's port scan checks"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    print(f"🌍 Internal web server started on port {port} for Render health checks.")
    server.serve_forever()

def clean_old_cache():
    """Flushes the duplicate storage set every hour to keep server RAM fast and minimal"""
    while True:
        time.sleep(3600)
        with cache_lock:
            processed_messages_cache.clear()
            print("🧹 Internal duplicate message tracking cache cleared successfully.")

def send_to_whatsapp(text_message):
    """Dispatches the clean text update to your WhatsApp Community completely for free"""
    url = f"https://green-api.com{GREEN_API_ID}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": WHATSAPP_CHAT_ID,
        "message": text_message
    }
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            print("🟢 Successfully broadcasted to your WhatsApp Community!")
        else:
            print(f"⚠️ WhatsApp API returned an issue: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Failed to reach Green-API cloud router: {e}")

def reformat_text(raw_text):
    """Dynamically structures text into an explicit Job Alert or News Flash layout"""
    clean_text = re.sub(r'[*_`~]', '', raw_text).strip()
    text_lower = clean_text.lower()
    news_triggers = ['عاجل', 'رسميا', 'رسمياً', 'قرارات', 'قرار', 'توطين', 'سعودة', 'الموارد البشرية']
    
    if any(trigger in text_lower for trigger in news_triggers):
        header_title = "🚨 **تحديث سوق العمل | MARKET NEWS FLASH**"
    else:
        header_title = "💼 **فرصة عمل جديدة | NEW JOB OPPORTUNITY**"
    
    arranged_template = (
        f"{header_title}\n"
        "📢 **قناة: سم مع مهند**\n"
        "──────────────────────\n\n"
        f"{clean_text}\n\n"
        "──────────────────────\n"
        "🚀 تابعوا **سم مع مهند** للمزيد من الفرص والأخبار اليومية!\n\n"
        "#وظائف #وظائف_السعودية #أخبار_التوظيف #توظيف #سم_مع_مهند"
    )
    return arranged_template

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def filter_and_forward(event):
    original_text = event.message.message
    if not original_text:
        return

    # 🌟 ANTI-DUPLICATE INTERCEPTION STRATEGY
    # Formats text structure to check if this core layout has been processed recently
    simplified_text = "".join(original_text.split()).lower()[:150]
    
    with cache_lock:
        if simplified_text in processed_messages_cache:
            print("⏳ Duplicate post intercepted from secondary source channel. Skipping...")
            return
        processed_messages_cache.add(simplified_text)

    searchable_content = [original_text.lower()]

    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityTextUrl):
                searchable_content.append(entity.url.lower())
            elif isinstance(entity, MessageEntityUrl):
                offset = entity.offset
                length = entity.length
                url_text = original_text[offset:offset+length]
                searchable_content.append(url_text.lower())

    combined_search_text = " ".join(searchable_content)

    # MATCH KEYWORD FILTER
    if any(job in combined_search_text for job in JOB_KEYWORDS):
        formatted_text = reformat_text(original_text)
        
        # 1. Dispatch Post to Your Telegram Destination Channel
        if event.message.media and isinstance(event.message.media, MessageMediaPhoto):
            await client.send_message(DESTINATION_CHANNEL, formatted_text, file=event.message.media)
            print("📸 Successfully formatted and posted an image-job to Telegram!")
        else:
            await client.send_message(DESTINATION_CHANNEL, formatted_text, link_preview=False)
            print("📝 Successfully formatted and posted a text-job to Telegram!")
        
        # 2. 🌟 Dispatch Same Post Natively to Your WhatsApp Community
        # Replaces dual asterisks (Telegram style) with single ones (WhatsApp style bolding)
        whatsapp_clean = formatted_text.replace('**', '*') 
        threading.Thread(target=send_to_whatsapp, args=(whatsapp_clean,), daemon=True).start()
        
    else:
        # If it didn't match your filters, release it from cache to let future accurate edits clear
        with cache_lock:
            processed_messages_cache.discard(simplified_text)
        print("⏳ Post did not match job or link keywords. Skipping...")

def main():
    # Start server threads right before initializing the live Telethon listener loop
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=clean_old_cache, daemon=True).start()
    
    client.start()
    print("Anti-branding dual job bot is running and listening cleanly...")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
