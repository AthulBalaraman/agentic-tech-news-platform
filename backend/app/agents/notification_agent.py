import httpx
from typing import List
from ..models.insight import Insight
from ..models.trend import Trend
from ..core.config import get_settings

settings = get_settings()

class NotificationAgent:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_daily_digest(self, insights: List[Insight], trends: List[Trend]):
        if not self.bot_token or not self.chat_id:
            print("⚠️ Telegram credentials missing. Skipping notification.")
            return

        if not insights and not trends:
            print("ℹ️ No new insights or trends to report today.")
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

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True # Keeps the chat clean from massive link previews
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, json=payload)
                if response.status_code != 200:
                    print(f"⚠️ Failed to send Telegram message: {response.text}")
                else:
                    print("✅ Telegram digest sent successfully.")
            except Exception as e:
                print(f"⚠️ Telegram notification connection error: {e}")
