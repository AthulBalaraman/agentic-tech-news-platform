from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from .github_agent import GitHubAgent
from .news_agent import NewsAgent
from .memory_agent import MemoryAgent
from .summarizer_agent import SummarizerAgent
from .evaluator_agent import EvaluatorAgent
from .trend_agent import TrendAgent
from .notification_agent import NotificationAgent
from ..core.database import db
from ..core.vector_store import vector_store
from ..models.raw_data import RawData
from ..models.insight import Insight
from ..models.trend import Trend

class AgentState(TypedDict):
    github_results: List[RawData]
    news_results: List[RawData]
    unique_items: List[RawData]
    insights: List[Insight]
    trends: List[Trend]
    status: str

async def collect_github(state: AgentState) -> Dict[str, Any]:
    agent = GitHubAgent()
    results = await agent.fetch_trending_repos()
    return {"github_results": results}

async def collect_news(state: AgentState) -> Dict[str, Any]:
    agent = NewsAgent()
    results = await agent.fetch_news()
    return {"news_results": results}

async def save_raw_db(state: AgentState) -> Dict[str, Any]:
    all_data = state.get("github_results", []) + state.get("news_results", [])
    if all_data:
        docs = [data.model_dump() for data in all_data]
        await db.db["raw_data"].insert_many(docs)
    return {"status": f"Saved {len(all_data)} raw items"}

async def filter_memory(state: AgentState) -> Dict[str, Any]:
    agent = MemoryAgent()
    all_data = state.get("github_results", []) + state.get("news_results", [])
    unique = agent.filter_duplicates(all_data)
    return {"unique_items": unique, "status": f"Filtered to {len(unique)} novel items"}

async def process_and_evaluate_items(state: AgentState) -> Dict[str, Any]:
    summarizer = SummarizerAgent()
    evaluator = EvaluatorAgent()
    unique_items = state.get("unique_items", [])
    valid_insights = []
    
    for item in unique_items:
        # Step 1: Initial Summary
        insight = await summarizer.summarize(item)
        if not insight:
            continue
            
        # Step 2: Quality Control (Critic Agent)
        evaluation = await evaluator.evaluate(item, insight)
        
        # Step 3: Refine Loop (Max 1 retry for MVP)
        if evaluation.get("score", 0) < 70:
            print(f"🔄 Refining {item.title}. Feedback: {evaluation.get('feedback')}")
            refined_insight = await summarizer.summarize(item, feedback=evaluation.get("feedback"))
            if refined_insight:
                # We do not evaluate the second time to prevent infinite loops, we trust the refined version
                valid_insights.append(refined_insight)
        else:
            valid_insights.append(insight)
            
    return {"insights": valid_insights, "status": f"Generated {len(valid_insights)} verified insights"}

async def detect_trends(state: AgentState) -> Dict[str, Any]:
    agent = TrendAgent()
    insights = state.get("insights", [])
    trends = await agent.detect_trends(insights)
    
    if trends:
        # Save trends to DB
        docs = [t.model_dump() for t in trends]
        await db.db["trends"].insert_many(docs)
        
    return {"trends": trends, "status": f"Detected {len(trends)} macro trends"}

async def save_insights_and_notify(state: AgentState) -> Dict[str, Any]:
    insights = state.get("insights", [])
    trends = state.get("trends", [])
    
    # Save Insights to DB & Chroma
    if insights:
        docs = [i.model_dump() for i in insights]
        await db.db["insights"].insert_many(docs)
        
        for i in insights:
            vector_context = f"Title: {i.title} Summary: {i.what_is_it} Impact: {i.why_it_matters}"
            vector_store.add_insight(
                id=i.external_id,
                text=vector_context,
                metadata={"title": i.title, "source": i.source}
            )

    # Trigger Notification
    notifier = NotificationAgent()
    await notifier.send_daily_digest(insights, trends)
            
    return {"status": "Execution Complete: Database Updated & Notifications Sent"}

def create_orchestrator_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("collect_github", collect_github)
    workflow.add_node("collect_news", collect_news)
    workflow.add_node("save_raw_db", save_raw_db)
    workflow.add_node("filter_memory", filter_memory)
    workflow.add_node("process_and_evaluate_items", process_and_evaluate_items)
    workflow.add_node("detect_trends", detect_trends)
    workflow.add_node("save_insights_and_notify", save_insights_and_notify)
    
    workflow.set_entry_point("collect_github")
    workflow.add_edge("collect_github", "collect_news")
    workflow.add_edge("collect_news", "save_raw_db")
    workflow.add_edge("save_raw_db", "filter_memory")
    workflow.add_edge("filter_memory", "process_and_evaluate_items")
    workflow.add_edge("process_and_evaluate_items", "detect_trends")
    workflow.add_edge("detect_trends", "save_insights_and_notify")
    workflow.add_edge("save_insights_and_notify", END)
    
    return workflow.compile()

orchestrator = create_orchestrator_graph()
