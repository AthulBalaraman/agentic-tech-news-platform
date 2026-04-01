import httpx
from typing import List
from ..models.insight import Insight
from ..models.trend import Trend
from ..core.config import get_settings
from ..core.database import db

settings = get_settings()

class NotificationAgent:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def get_all_subscribers(self) -> List[int]:
        """Fetch all approved chat IDs from the database."""
        # Always include the default admin chat_id from settings if it exists
        subscribers = [self.chat_id] if self.chat_id else []
        try:
            if db.db is not None:
                # ONLY fetch subscribers with status "approved"
                cursor = db.db["subscribers"].find({"status": "approved"}, {"chat_id": 1})
                db_subs = await cursor.to_list(length=1000)
                for sub in db_subs:
                    cid = sub.get("chat_id")
                    if cid and cid not in subscribers:
                        subscribers.append(cid)
        except Exception as e:
            print(f"⚠️ Error fetching subscribers from DB: {e}")
        return subscribers

    async def send_admin_alert(self, message: str, reply_markup: dict = None):
        if not self.bot_token:
            print("⚠️ Telegram bot token missing. Skipping notification.")
            return

        chat_ids = await self.get_all_subscribers()
        if not chat_ids:
            # If no approved subs, at least try to send to the admin chat_id from env
            if self.chat_id:
                chat_ids = [self.chat_id]
            else:
                print("⚠️ No subscribers or admin chat ID found.")
                return

        async with httpx.AsyncClient() as client:
            for cid in chat_ids:
                payload = {
                    "chat_id": cid,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                if reply_markup:
                    payload["reply_markup"] = reply_markup
                    
                try:
                    response = await client.post(self.url, json=payload)
                    if response.status_code != 200:
                        print(f"⚠️ Failed to notify {cid}: {response.text}")
                except Exception as e:
                    print(f"⚠️ Connection error for {cid}: {e}")

    async def send_daily_digest(self, insights: List[Insight], trends: List[Trend]):
        if not self.bot_token:
            print("⚠️ Telegram bot token missing. Skipping notification.")
            return

        if not insights and not trends:
            print("ℹ️ No new insights or trends to report today.")
            return

        chat_ids = await self.get_all_subscribers()
        if not chat_ids:
            print("⚠️ No subscribers found to notify.")
            return

        # Build the message payload (Markdown formatted)
        message = "🤖 *Daily AI Tech Intel Digest*\n\n"
        
        if trends:
            message += "📈 *Macro Trends Identified:*\n"
            for t in trends:
                message += f"• *{t.trend_name}*: {t.description}\n"
            message += "\n"
            
        if insights:
            message += "💡 *New Verified Insights:*\n"
            for i in insights:
                # Markdown link format: [Text](URL)
                message += f"• [{i.title}]({i.external_id})\n  _{i.what_is_it}_\n"

        async with httpx.AsyncClient() as client:
            for cid in chat_ids:
                payload = {
                    "chat_id": cid,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                try:
                    response = await client.post(self.url, json=payload)
                    if response.status_code != 200:
                        print(f"⚠️ Failed to notify {cid}: {response.text}")
                except Exception as e:
                    print(f"⚠️ Connection error for {cid}: {e}")
