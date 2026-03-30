from fastapi import FastAPI
from .core.database import connect_to_mongo, close_mongo_connection
from .agents.orchestrator import orchestrator

app = FastAPI(title="AI Tech Intelligence Platform API")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
