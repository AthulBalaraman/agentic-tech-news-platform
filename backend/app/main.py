from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.database import db, connect_to_mongo, close_mongo_connection
from .core.vector_store import vector_store
from .agents.orchestrator import orchestrator
from .agents.notification_agent import NotificationAgent

app = FastAPI(title="AI Tech Intelligence Platform API")

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

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

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
async def get_insights(status: str = "pending"):
    """Fetch insights based on status (pending, approved, rejected)."""
    cursor = db.db["insights"].find({"status": status}).sort("created_at", -1)
    insights = await cursor.to_list(length=100)
    
    # Convert ObjectId to string for JSON serialization
    for doc in insights:
        doc["_id"] = str(doc["_id"])
    return insights

@app.post("/api/insights/{external_id}/approve")
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
async def get_trends():
    """Fetch identified macro trends."""
    cursor = db.db["trends"].find().sort("detected_at", -1)
    trends = await cursor.to_list(length=20)
    
    for doc in trends:
        doc["_id"] = str(doc["_id"])
    return trends
