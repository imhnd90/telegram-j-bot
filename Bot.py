import re
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageEntityTextUrl, MessageEntityUrl

# --- CONFIGURATION ---
API_ID = 35769422  # <-- Your API ID
API_HASH = '9f5fdb40f517efb629843d96ddaa5a71'  # <-- Your API Hash

SOURCE_CHANNELS = [
    '@ewdifh',
    '@cd4cd',
    '@teleworksjobs',
    '@wadhefadotcom',
    '@i8mhnd'
]

DESTINATION_CHANNEL = '@sminbox'  

JOB_KEYWORDS = [
    'stc', 'الاتصالات', 'شركة', 'أرامكو', 'ارامكو', 'بنك', 'سابك', 'وزارة', 'الوزارة', 'حكومي',
    'عاجل', 'رسميا', 'رسمياً', 'أعلنت', 'اعلت', 'يعلن', 'تعلن', 'شواغر', 'شاغر', 'شاغرة',
    'وظيفة', 'وظايف', 'وظائف', 'توظيف', 'تدريب', 'فرصة عمل', 'فرص عمل', 'مطلوب', 'مطلوبة', 
    'بايثون', 'عن بعد', 'عن_بعد', 'مطور', 'مهندس', 'برمجة', 'برمجيات', 'تقنية', 'معلومات',
    'python', 'remote', 'developer', 'engineer', 'django', 'backend', 'frontend', 'fullstack',
    'software', 'hiring', 'vacancy', 'job', 'jobs', 'internship', 'careers', 'career', 'apply'
]

PROMO_KEYWORDS = [
    # Leave empty or add promotional block keywords here if needed later
]

client = TelegramClient('job_forwarder_session', API_ID, API_HASH)

# 🌟 RENDER PORT BINDING FIX: Dummy web server class
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

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
    """Structures text into a beautifully arranged, professional layout"""
    clean_text = re.sub(r'[*_`~]', '', raw_text).strip()
    
    arranged_template = (
        "💼 **فرصة عمل جديدة | NEW JOB OPPORTUNITY**\n"
        "📢 **قناة: سم مع مهند**\n"
        "──────────────────────\n\n"
        f"{clean_text}\n\n"
        "──────────────────────\n"
        "🚀 تابعوا **سم مع مهند** للمزيد من الفرص اليومية!"
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
