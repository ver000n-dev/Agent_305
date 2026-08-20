import os
import time
import threading
import requests
import feedparser
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# Health Check لـ Render
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

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
    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json={"content": message}
        )

        print("Discord:", response.status_code)

    except Exception as e:
        print("Discord Error:", e)

# ==========================================
# RSS Sources
# ==========================================
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

COINS = [
    "XRP",
    "ADA",
    "HBAR",
    "WLD"
]

seen_links = set()

print("🚀 Crypto Agent Started")

send_discord_message("✅ Agent Started Successfully")

# ==========================================
# Main Loop
# ==========================================
while True:

    try:

        for feed_url in RSS_FEEDS:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries:

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                if not link:
                    continue

                if link in seen_links:
                    continue

                text = f"{title} {summary}".upper()

                matched_coin = None

                for coin in COINS:
                    if coin in text:
                        matched_coin = coin
                        break

                if matched_coin:

                    msg = f"""
🪙 {matched_coin}

📰 {title}

🔗 {link}
"""

                    send_discord_message(msg)

                    seen_links.add(link)

                    print("News Sent:", matched_coin)

        print("Waiting 30 minutes...")

    except Exception as e:
        print("Error:", e)

    time.sleep(1800)
