from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from bson import ObjectId
from datetime import datetime
import httpx
from .core.config import get_settings
from .core.database import db, connect_to_mongo, close_mongo_connection
from .core.vector_store import vector_store
from .agents.orchestrator import orchestrator
from .agents.notification_agent import NotificationAgent

settings = get_settings()
app = FastAPI(title="AI Tech Intelligence Platform API")

# Initialize the scheduler
scheduler = AsyncIOScheduler()

# Global state for Telegram polling
TELEGRAM_OFFSET = 0

# Define the scheduled task
async def run_scheduled_collection():
    print("⏰ Starting scheduled AI intelligence collection...")
    initial_state = {
        "github_results": [],
        "news_results": [],
        "status": "starting"
    }
    try:
        result = await orchestrator.ainvoke(initial_state)
        print(f"✅ Scheduled collection completed with status: {result['status']}")
    except Exception as e:
        print(f"❌ Scheduled collection failed: {e}")

async def poll_telegram_updates():
    """Background task to listen for /start commands and admin callback approvals."""
    global TELEGRAM_OFFSET
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        async with httpx.AsyncClient() as client:
            # We use a 15s timeout because the Telegram poll itself waits for 10s
            params = {"offset": TELEGRAM_OFFSET + 1, "timeout": 10}
            response = await client.get(url, params=params, timeout=15.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for update in data.get("result", []):
                        TELEGRAM_OFFSET = update["update_id"]
                        
                        # 1. Handle New Join Requests (/start)
                        message = update.get("message")
                        if message and "text" in message:
                            chat_id = message["chat"]["id"]
                            text = message["text"]
                            user = message.get("from", {})
                            full_name = f"{user.get('first_name', 'User')} {user.get('last_name', '')}".strip()
                            
                            if text.startswith("/start"):
                                print(f"👤 Processing /start from {full_name} (ID: {chat_id})...")
                                
                                await db.db["subscribers"].update_one(
                                    {"chat_id": chat_id},
                                    [
                                        {"$set": {
                                            "chat_id": chat_id,
                                            "user_name": full_name,
                                            "registered_at": {"$ifNull": ["$registered_at", datetime.utcnow()]},
                                            "status": {"$ifNull": ["$status", "pending"]}
                                        }}
                                    ],
                                    upsert=True
                                )
                                
                                # Alert Admin with Inline Buttons
                                notifier = NotificationAgent()
                                reply_markup = {
                                    "inline_keyboard": [[
                                        {"text": "✅ Approve", "callback_data": f"approve:{chat_id}"},
                                        {"text": "❌ Reject", "callback_data": f"reject:{chat_id}"}
                                    ]]
                                }
                                await notifier.send_admin_alert(
                                    f"👤 *New Join Request:*\n{full_name} ({chat_id}) is requesting access.",
                                    reply_markup=reply_markup
                                )
                                
                                # Send pending message to user
                                await client.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                                    "chat_id": chat_id,
                                    "text": "⏳ *Access Request Received*\n\nYour request has been sent to the admin for approval. You will be notified once access is granted.",
                                    "parse_mode": "Markdown"
                                })

                        # 2. Handle Admin Callbacks (Approve/Reject buttons)
                        callback = update.get("callback_query")
                        if callback:
                            callback_data = callback.get("data", "")
                            admin_chat_id = callback["message"]["chat"]["id"]
                            message_id = callback["message"]["message_id"]
                            
                            if ":" in callback_data:
                                action, target_id = callback_data.split(":")
                                target_id = int(target_id)
                                
                                if action == "approve":
                                    await approve_subscriber(target_id)
                                    status_text = "✅ Approved"
                                else:
                                    await reject_subscriber(target_id)
                                    status_text = "❌ Rejected"
                                
                                # Update the admin's message to show it's done
                                original_text = callback["message"]["text"]
                                await client.post(f"https://api.telegram.org/bot{bot_token}/editMessageText", json={
                                    "chat_id": admin_chat_id,
                                    "message_id": message_id,
                                    "text": f"{original_text}\n\n*Status:* {status_text}",
                                    "parse_mode": "Markdown"
                                })
                                
                                # Answer callback to remove "loading" state on button
                                await client.post(f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery", json={
                                    "callback_query_id": callback["id"],
                                    "text": f"User {status_text}"
                                })
            elif response.status_code == 409:
                print("⚠️ Telegram Conflict (409): Another bot listener is likely running. Close other terminal windows.")
            elif response.status_code == 401:
                print("⚠️ Telegram Unauthorized (401): Your BOT_TOKEN is invalid.")
            else:
                print(f"⚠️ Telegram Polling Error ({response.status_code}): {response.text}")

    except httpx.ReadTimeout:
        # Long polling timeouts are normal, just continue
        pass
    except Exception as e:
        print(f"⚠️ Unexpected polling exception: {type(e).__name__}: {e}")

# Add CORS middleware to allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for MVP. Update this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    
    # Schedule jobs for 10 AM and 4 PM (16:00)
    scheduler.add_job(run_scheduled_collection, CronTrigger(hour=10, minute=0))
    scheduler.add_job(run_scheduled_collection, CronTrigger(hour=16, minute=0))
    
    # Add the Telegram polling task to run every 10 seconds
    if settings.TELEGRAM_BOT_TOKEN:
        scheduler.add_job(poll_telegram_updates, IntervalTrigger(seconds=10))
        print("🚀 Telegram bot listener started (polling every 10s).")
    
    scheduler.start()
    print("🚀 Scheduler started: Collection scheduled for 10:00 AM and 4:00 PM daily.")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    scheduler.shutdown()
    print("🛑 Scheduler shut down.")

@app.post("/api/bot/register")
async def register_subscriber(chat_id: int, user_name: str = "Unknown"):
    """Register a new Telegram chat ID. Defaults to pending. (Kept for manual overrides/API usage)"""
    await db.db["subscribers"].update_one(
        {"chat_id": chat_id},
        [
            {"$set": {
                "chat_id": chat_id,
                "user_name": user_name,
                "registered_at": {"$ifNull": ["$registered_at", datetime.utcnow()]},
                "status": {"$ifNull": ["$status", "pending"]}
            }}
        ],
        upsert=True
    )
    
    notifier = NotificationAgent()
    await notifier.send_admin_alert(f"👤 *New Join Request:*\n{user_name} ({chat_id}) is requesting access.\n_Check your dashboard to approve._")
    
    return {"message": "Subscriber request logged"}

@app.get("/api/subscribers")
async def get_subscribers(status: str = "pending"):
    """Fetch subscribers based on status."""
    cursor = db.db["subscribers"].find({"status": status}).sort("registered_at", -1)
    subs = await cursor.to_list(length=100)
    for doc in subs:
        doc["_id"] = str(doc["_id"])
    return subs

@app.post("/api/subscribers/{chat_id}/approve")
async def approve_subscriber(chat_id: int):
    """Approve a pending subscriber."""
    await db.db["subscribers"].update_one({"chat_id": chat_id}, {"$set": {"status": "approved"}})
    
    # Notify the user they were approved
    import httpx
    notifier = NotificationAgent()
    if notifier.bot_token:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"https://api.telegram.org/bot{notifier.bot_token}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": "🎉 *Access Granted!*\n\nThe admin has approved your request. You will now receive AI Tech Intel updates.",
                    "parse_mode": "Markdown"
                })
        except Exception:
            pass
            
    return {"message": "Subscriber approved"}

@app.post("/api/subscribers/{chat_id}/reject")
async def reject_subscriber(chat_id: int):
    """Reject a pending subscriber."""
    await db.db["subscribers"].update_one({"chat_id": chat_id}, {"$set": {"status": "rejected"}})
    return {"message": "Subscriber rejected"}

@app.get("/")
async def root():
    return {"message": "AI Tech Intelligence Platform API is running"}

@app.post("/trigger-collection")
async def trigger_collection():
    initial_state = {
        "github_results": [],
        "news_results": [],
        "status": "starting"
    }
    result = await orchestrator.ainvoke(initial_state)
    return {"message": "Collection completed", "status": result["status"]}

# --- UI Endpoints (Sprint 4) ---

@app.get("/api/insights")
async def get_insights(status: str = "pending", page: int = 1, limit: int = 10):
    """Fetch insights based on status (pending, approved, rejected) with pagination."""
    skip = (page - 1) * limit
    cursor = db.db["insights"].find({"status": status}).sort("created_at", -1).skip(skip).limit(limit)
    insights = await cursor.to_list(length=limit)
    
    total = await db.db["insights"].count_documents({"status": status})
    
    # Convert ObjectId to string for JSON serialization
    for doc in insights:
        doc["_id"] = str(doc["_id"])
        
    return {
        "items": insights,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.post("/api/insights/{external_id:path}/approve")
async def approve_insight(external_id: str):
    """Approve an insight, save it to Vector DB, and send to Telegram."""
    # Find the insight
    insight_doc = await db.db["insights"].find_one({"external_id": external_id})
    if not insight_doc:
        raise HTTPException(status_code=404, detail="Insight not found")
        
    if insight_doc.get("status") == "approved":
        return {"message": "Insight already approved"}

    # Update status in DB
    await db.db["insights"].update_one(
        {"external_id": external_id},
        {"$set": {"status": "approved"}}
    )
    
    # Add to Semantic Memory (Vector Store)
    vector_context = f"Title: {insight_doc['title']} Summary: {insight_doc['what_is_it']} Impact: {insight_doc['why_it_matters']}"
    vector_store.add_insight(
        id=insight_doc['external_id'],
        text=vector_context,
        metadata={"title": insight_doc['title'], "source": insight_doc['source']}
    )
    
    # Trigger notification logic (For simplicity, we just send a single alert here)
    # In a full production system, you might batch approvals and send one digest
    notifier = NotificationAgent()
    message = f"💡 *Approved Insight:*\n[{insight_doc['title']}]({insight_doc['external_id']})\n_{insight_doc['what_is_it']}_"
    await notifier.send_admin_alert(message) # Using admin alert method for immediate single pushes

    return {"message": "Insight approved and indexed in Vector DB"}

@app.get("/api/trends")
async def get_trends(page: int = 1, limit: int = 10):
    """Fetch identified macro trends with pagination."""
    skip = (page - 1) * limit
    cursor = db.db["trends"].find().sort("detected_at", -1).skip(skip).limit(limit)
    trends = await cursor.to_list(length=limit)
    
    total = await db.db["trends"].count_documents({})
    
    for doc in trends:
        doc["_id"] = str(doc["_id"])
        
    return {
        "items": trends,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@app.post("/api/trends/{trend_id}/send")
async def send_trend(trend_id: str):
    """Send a detected macro trend to the Telegram bot."""
    try:
        doc_id = ObjectId(trend_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trend ID format")

    trend_doc = await db.db["trends"].find_one({"_id": doc_id})
    if not trend_doc:
        raise HTTPException(status_code=404, detail="Trend not found")
        
    notifier = NotificationAgent()
    related = ", ".join(trend_doc.get('related_insights', []))
    message = f"📈 *Macro Trend Alert: {trend_doc['trend_name']}*\n\n{trend_doc['description']}\n\n_Related Concepts:_ {related}"
    
    await notifier.send_admin_alert(message)
    return {"message": "Trend sent to Telegram"}
