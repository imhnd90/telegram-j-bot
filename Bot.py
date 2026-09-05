import re
import os
import threading
import time
import requests  
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageEntityTextUrl, MessageEntityUrl
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURATION ---
API_ID = 35769422  
API_HASH = '9f5fdb40f517efb629843d96ddaa5a71'  

# 🌟 GREEN-API WHATSAPP CREDENTIALS
GREEN_API_ID = '710522728838'            
GREEN_API_TOKEN = '6dbb40f208984ebab3908788583748b822b453ad99bb487da5'    
WHATSAPP_CHAT_ID = '120363428984270611@g.us'   

SOURCE_CHANNELS = [
    '@ewdifh', '@cd4cd', '@teleworksjobs', '@wadhefadotcom', '@i8mhnd',
    '@jobs4ksa', '@hrgksa', '@saudijobs24', '@jobs2ksa'
]

DESTINATION_CHANNEL = '@sammhnd'  

JOB_KEYWORDS = [
    'عاجل', 'رسميا', 'رسمياً', 'وزارة', 'الوزارة', 'الموارد البشرية', 'قرارات', 'قرار', 'توطين', 
    'سعودة', 'هدف', 'صندوق', 'بيان رسمي', 'تعلن', 'يعلن', 'أعلنت', 'اعلت', 'mhrsd', 'hrdf', 'qiwa',
    'شركة', 'أرامكو', 'ارامكو', 'stc', 'الاتصالات', 'نيوم', 'neom', 'سابك', 'البحر الأحمر', 
    'روشن', 'المربع الجديد', 'بنك', 'مصرف', 'الراجحي', 'الأهلي', 'طيران', 'الخطوط', 'مستشفى',
    'وظيفة', 'وظايف', 'وظائف', 'شواغر', 'شاغر', 'شاغرة', 'توظيف', 'تدريب', 'فرصة عمل', 'فرص عمل', 
    'مطلوب', 'مطلوبة', 'برنامج', 'حكومي', 'اداري', 'إداري', 'استقبال', 'خدمة عملاء', 'مبيعات',
    'hiring', 'vacancy', 'job', 'jobs', 'internship', 'career', 'careers', 'apply', 'recruitment',
    'مهندس', 'هندسة', 'محاسب', 'محاسبة', 'قانوني', 'محامي', 'تقنية', 'معلومات', 'برمجة', 'مطور',
    'امن سيبراني', 'ذكاء اصطناعي', 'شبكات', 'سلاسل الإمداد', 'لوجستي', 'مستودع', 'مشتريات',
    'engineer', 'accounting', 'finance', 'logistics', 'procurement', 'developer', 'python'
]

PROMO_KEYWORDS = []

# 🌟 DUAL MEMORY CACHE (TRACKS TEXT AND UNIQUE APPLICATION LINKS)
processed_text_cache = set()
processed_links_cache = set()
cache_lock = threading.Lock()

client = TelegramClient('render_cloud_session', API_ID, API_HASH)

class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", "18")
        self.end_headers()
        self.wfile.write(b"Bot is active 24/7")
    def log_message(self, format, *args): return

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

def clean_old_cache():
    """Flushes background tracking caches every hour to preserve server memory"""
    while True:
        time.sleep(3600)
        with cache_lock:
            processed_text_cache.clear()
            processed_links_cache.clear()
            print("🧹 Cache memory flushed successfully.")

def send_to_whatsapp(text_message):
    url = f"https://green-api.com{GREEN_API_ID}/sendMessage/{GREEN_API_TOKEN}"
    payload = {
        "chatId": WHATSAPP_CHAT_ID,
        "message": text_message
    }
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📡 WhatsApp API Router Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Green-API gateway: {e}")

def reformat_text(raw_text, mode="telegram"):
    clean_text = re.sub(r'[*_`~]', '', raw_text).strip()
    text_lower = clean_text.lower()
    news_triggers = ['عاجل', 'رسميا', 'رسمياً', 'قرارات', 'قرار', 'توطين', 'سعودة', 'الموارد البشرية']
    
    if any(trigger in text_lower for trigger in news_triggers):
        title_tg = "🚨 **تحديث سوق العمل | MARKET NEWS FLASH**"
        title_wa = "🚨 *تحديث سوق العمل | MARKET NEWS FLASH*"
    else:
        title_tg = "💼 **فرصة عمل جديدة | NEW JOB OPPORTUNITY**"
        title_wa = "💼 *فرصة عمل جديدة | NEW JOB OPPORTUNITY*"
    
    if mode == "whatsapp":
        return (
            f"{title_wa}\n"
            "📢 *قناة: سم مع مهند*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{clean_text}\n\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            "🚀 تابعوا *سم مع مهند* للمزيد من الفرص والأخبار اليومية!\n\n"
            "#وظائف #وظائف_السعودية #أخبار_التوظيف #توظيف #سم_مع_مهند"
        )
    else:
        return (
            f"{title_tg}\n"
            "📢 **قناة: سم مع مهند**\n"
            "──────────────────────\n\n"
            f"{clean_text}\n\n"
            "──────────────────────\n"
            "🚀 تابعوا **سم مع مهند** للمزيد من الفرص والأخبار اليومية!\n\n"
            "#وظائف #وظائف_السعودية #أخبار_التوظيف #توظيف #سم_مع_مهند"
        )

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def filter_and_forward(event):
    original_text = event.message.message
    if not original_text: return

    # 1. Check text-based duplicates
    simplified_text = "".join(original_text.split()).lower()[:150]
    with cache_lock:
        if simplified_text in processed_text_cache:
            print("⏳ Text-based duplicate intercepted. Skipping...")
            return

    # 2. 🌟 Smart Check: Extract links to catch rewritten duplicates
    extracted_urls = []
    if event.message.entities:
        for entity in event.message.entities:
            if isinstance(entity, MessageEntityTextUrl):
                extracted_urls.append(entity.url.lower())
            elif isinstance(entity, MessageEntityUrl):
                offset = entity.offset
                length = entity.length
                url_text = original_text[offset:offset+length]
                extracted_urls.append(url_text.lower())

    # Skip external tracking steps or channel links to purely catch core application endpoints
    valid_job_links = [u for u in extracted_urls if "t.me" not in u and "whatsapp" not in u]

    with cache_lock:
        # If any found application link has been processed recently, skip the post completely!
        for link in valid_job_links:
            if link in processed_links_cache:
                print(f"⏳ Link-based duplicate caught ({link}). Skipping...")
                return
        
        # Lock strings into cache sets
        processed_text_cache.add(simplified_text)
        for link in valid_job_links:
            processed_links_cache.add(link)

    searchable_content = [original_text.lower()] + extracted_urls
    combined_search_text = " ".join(searchable_content)

    if any(job in combined_search_text for job in JOB_KEYWORDS):
        tg_text = reformat_text(original_text, mode="telegram")
        if event.message.media and isinstance(event.message.media, MessageMediaPhoto):
            await client.send_message(DESTINATION_CHANNEL, tg_text, file=event.message.media)
        else:
            await client.send_message(DESTINATION_CHANNEL, tg_text, link_preview=False)
        
        wa_text = reformat_text(original_text, mode="whatsapp")
        threading.Thread(target=send_to_whatsapp, args=(wa_text,), daemon=True).start()
    else:
        with cache_lock:
            processed_text_cache.discard(simplified_text)
            for link in valid_job_links:
                processed_links_cache.discard(link)

def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=clean_old_cache, daemon=True).start()
    client.start()
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
