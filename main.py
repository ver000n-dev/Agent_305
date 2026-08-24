import os
import time
import threading
import requests
import feedparser
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# Health Check لـ Render (GET + HEAD)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    # إلغاء طباعة طلبات الـ HTTP في السجلات لتنظيف الـ Logs
    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ==========================================
# Discord Webhook
# ==========================================
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_message(message):
    if not DISCORD_WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL is not set!")
        return
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": message},
            timeout=10
        )
        print("Discord status:", response.status_code)
    except Exception as e:
        print("Discord Error:", e)

# ==========================================
# RSS Sources & Coin Keywords
# ==========================================
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed",
    "https://www.newsbtc.com/feed/",
    "https://blockworks.co/feed"
]

COINS = [
    "XRP", "RIPPLE",
    "ADA", "CARDANO",
    "HBAR", "HEDERA",
    "WLD", "WORLDCOIN"
]

seen_links = set()

print("🚀 Crypto Agent Started")
send_discord_message("✅ Crypto Agent Started Successfully")

# ==========================================
# Main Loop (Every 30 Minutes)
# ==========================================
while True:
    try:
        print("=" * 50)
        print("NEW SCAN STARTED")
        print("Checking RSS feeds...")

        for feed_url in RSS_FEEDS:
            print(f"Checking: {feed_url}")
            try:
                # جلب البيانات مع وضع timeout لمنع التجميد
                feed = feedparser.parse(feed_url)
                print(f"Articles Found: {len(feed.entries)}")

                for entry in feed.entries:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    link = entry.get("link", "")

                    if not link or link in seen_links:
                        continue

                    text = f"{title} {summary}".upper()

                    matched_coin = None
                    for coin in COINS:
                        if coin in text:
                            matched_coin = coin
                            break

                    if matched_coin:
                        print(f"MATCH FOUND: {matched_coin}")
                        print(f"TITLE: {title}")

                        msg = f"🪙 **{matched_coin}**\n\n📰 {title}\n\n🔗 {link}"
                        send_discord_message(msg)
                        seen_links.add(link)

            except Exception as feed_err:
                print(f"Error fetching {feed_url}: {feed_err}")

        print("SCAN COMPLETED")
        print("Sleeping 30 minutes...")

    except Exception as e:
        print("Main Loop Error:", e)

    # الانتظار لمدة 30 دقيقة (1800 ثانية)
    time.sleep(1800)
