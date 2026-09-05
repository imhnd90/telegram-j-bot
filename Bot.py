import re
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageEntityTextUrl, MessageEntityUrl

# --- CONFIGURATION ---
API_ID = 35769422  # <-- Your API ID
API_HASH = '9f5fdb40f517efb629843d96ddaa5a71'  # <-- Your API Hash
# 🌟 PASTE YOUR GREEN-API CREDENTIALS HERE:
GREEN_API_ID = '710522728838'            # <-- Paste your exact ID instance numbers here
GREEN_API_TOKEN = '6dbb40f208984ebab3908788583748b822b453ad99bb487da5'    # <-- Paste your long apiTokenInstance string here
WHATSAPP_CHAT_ID = '120363430663266458'   # <-- Paste your copied group/community ID ending in @g.us here

SOURCE_CHANNELS = [
    # Your current existing channels
    '@ewdifh',
    '@cd4cd',
    '@teleworksjobs',
    '@wadhefadotcom',
    '@i8mhnd',
    
    # 🌟 NEW: Master Job & Labor Market News Channels
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


PROMO_KEYWORDS = [
    # Leave empty or add promotional block keywords here if needed later
]

client = TelegramClient('render_cloud_session', API_ID, API_HASH)


# 🌟 RENDER PORT BINDING FIX: Dummy web server class
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # 🌟 FIXED COMPACT WEB RESPONSES FOR CRON-JOB
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", "18")
        self.end_headers()
        self.wfile.write(b"Bot is active 24/7")

    def log_message(self, format, *args):
        return  # Hides ping tracking logs to keep Render console clean



    # Override logging to keep Render console outputs clean
    def log_message(self, format, *args):
        return

def run_web_server():
    """Runs a tiny web server in the background to satisfy Render's port scan checks"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    print(f"🌍 Internal web server started on port {port} for Render health checks.")
    server.serve_forever()

def reformat_text(raw_text):
    """Dynamically structures text into an explicit Job Alert or News Flash layout"""
    clean_text = re.sub(r'[*_`~]', '', raw_text).strip()
    
    # Check if the message is a regulatory update or news breaking phrase
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

    # 1. ANTI-SPAM FILTER
    if PROMO_KEYWORDS and any(promo in combined_search_text for promo in PROMO_KEYWORDS):
        print("❌ Blocked a promotional / advertisement post.")
        return

    # 2. MATCH FILTER
    if any(job in combined_search_text for job in JOB_KEYWORDS):
        formatted_text = reformat_text(original_text)
        
        # If it's a real attached image file, forward it
        if event.message.media and isinstance(event.message.media, MessageMediaPhoto):
            await client.send_message(DESTINATION_CHANNEL, formatted_text, file=event.message.media)
            print("📸 Successfully formatted and posted an image-job to 'سم مع مهند'!")
        else:
            # Explicitly set link_preview=False to block external website preview boxes from appearing!
            await client.send_message(DESTINATION_CHANNEL, formatted_text, link_preview=False)
            print("📝 Successfully posted clean text without external preview boxes!")
    else:
        print("⏳ Post did not match job or link keywords. Skipping...")

def main():
    # 🌟 Start the background web server thread right before starting Telethon
    threading.Thread(target=run_web_server, daemon=True).start()
    
    client.start()
    print("Anti-branding job bot is running and listening cleanly...")
    client.run_until_disconnected()

if __name__ == '__main__':
    main()
