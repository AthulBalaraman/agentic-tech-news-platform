import time
import httpx
import sys
import os
from dotenv import load_dotenv

# Load .env if it exists
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token")
API_BASE_URL = "http://localhost:8000"

def listen_for_subscribers():
    print(f"🚀 Telegram Registration Listener Started...")
    print(f"Token: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:] if len(BOT_TOKEN) > 10 else ''}")
    print(f"Invite people to message your bot with /start to request access.")
    
    last_update_id = 0
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    # Test connection
    try:
        test_res = httpx.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if test_res.status_code == 200:
            bot_info = test_res.json()["result"]
            print(f"✅ Connected to Bot: @{bot_info['username']}")
        else:
            print(f"❌ Invalid Bot Token: {test_res.text}")
            return
    except Exception as e:
        print(f"❌ Could not connect to Telegram: {e}")
        return

    while True:
        try:
            params = {"offset": last_update_id + 1, "timeout": 30}
            response = httpx.get(telegram_url, params=params, timeout=35.0)
            
            if response.status_code != 200:
                print(f"❌ Telegram Error ({response.status_code}): {response.text}")
                time.sleep(5)
                continue
                
            data = response.json()
            for update in data.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message")
                
                if message and "text" in message:
                    chat_id = message["chat"]["id"]
                    text = message["text"]
                    
                    user = message.get("from", {})
                    first_name = user.get("first_name", "User")
                    last_name = user.get("last_name", "")
                    full_name = f"{first_name} {last_name}".strip()
                    
                    if text.startswith("/start"):
                        print(f"👤 Processing request from {full_name} (ID: {chat_id})...")
                        
                        # Register with our FastAPI backend
                        reg_url = f"{API_BASE_URL}/api/bot/register"
                        try:
                            reg_res = httpx.post(reg_url, params={"chat_id": chat_id, "user_name": full_name}, timeout=10.0)
                            
                            if reg_res.status_code == 200:
                                print(f"✅ Request logged for {full_name}!")
                                # Send a pending message back via Telegram
                                pending_msg = "⏳ *Access Request Received*\n\nYour request has been sent to the admin for approval. You will be notified once access is granted."
                                httpx.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": pending_msg,
                                    "parse_mode": "Markdown"
                                })
                            else:
                                print(f"❌ Backend Error: {reg_res.text}")
                        except Exception as e:
                            print(f"❌ Could not reach backend API at {API_BASE_URL}: {e}")

        except KeyboardInterrupt:
            print("\nStopping listener...")
            break
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BOT_TOKEN = sys.argv[1]
    
    if BOT_TOKEN == "your_telegram_bot_token" or not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env or arguments.")
        print("Usage: python register_bot.py <YOUR_BOT_TOKEN>")
    else:
        listen_for_subscribers()
