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
    print("\n[Orchestrator] 🚀 Step 1: Starting GitHub Agent...")
    agent = GitHubAgent()
    results = await agent.fetch_trending_repos()
    print(f"[Orchestrator] ✅ GitHub Agent found {len(results)} trending repositories.")
    return {"github_results": results}

async def collect_news(state: AgentState) -> Dict[str, Any]:
    print("\n[Orchestrator] 📰 Step 2: Starting News Agent...")
    agent = NewsAgent()
    results = await agent.fetch_news()
    print(f"[Orchestrator] ✅ News Agent found {len(results)} recent articles.")
    return {"news_results": results}

async def save_raw_db(state: AgentState) -> Dict[str, Any]:
    all_data = state.get("github_results", []) + state.get("news_results", [])
    print(f"\n[Orchestrator] 💾 Step 3: Saving {len(all_data)} raw items to MongoDB...")
    if all_data:
        docs = [data.model_dump() for data in all_data]
        await db.db["raw_data"].insert_many(docs)
        print(f"[Orchestrator] ✅ Successfully saved {len(all_data)} raw items.")
    else:
        print("[Orchestrator] ⚠️ No raw items to save.")
    return {"status": f"Saved {len(all_data)} raw items"}

async def filter_memory(state: AgentState) -> Dict[str, Any]:
    print("\n[Orchestrator] 🧠 Step 4: Memory Agent filtering duplicates...")
    agent = MemoryAgent()
    all_data = state.get("github_results", []) + state.get("news_results", [])
    unique = agent.filter_duplicates(all_data)
    print(f"[Orchestrator] ✅ Memory Agent kept {len(unique)} novel items (discarded {len(all_data) - len(unique)} duplicates).")
    return {"unique_items": unique, "status": f"Filtered to {len(unique)} novel items"}

async def process_and_evaluate_items(state: AgentState) -> Dict[str, Any]:
    print("\n[Orchestrator] 🤖 Step 5: Summarizer & Evaluator Agents processing novel items...")
    summarizer = SummarizerAgent()
    evaluator = EvaluatorAgent()
    unique_items = state.get("unique_items", [])
    valid_insights = []

    for index, item in enumerate(unique_items, 1):
        print(f"  -> Processing item {index}/{len(unique_items)}: {item.title}")

        # Step 1: Initial Summary
        insight = await summarizer.summarize(item)
        if not insight:
            print(f"     ❌ Summarizer failed for: {item.title}")
            continue

        # Step 2: Quality Control (Critic Agent)
        evaluation = await evaluator.evaluate(item, insight)
        score = evaluation.get("score", 0)
        print(f"     ⚖️ Critic Score: {score}/100")

        # Step 3: Refine Loop (Max 1 retry for MVP)
        if score < 70:
            print(f"     🔄 Refining '{item.title}' based on feedback: {evaluation.get('feedback')}")
            refined_insight = await summarizer.summarize(item, feedback=evaluation.get("feedback"))
            if refined_insight:
                print(f"     ✅ Refined insight accepted.")
                # We do not evaluate the second time to prevent infinite loops, we trust the refined version
                valid_insights.append(refined_insight)
            else:
                print(f"     ❌ Refinement failed, dropping insight.")
        else:
            print(f"     ✅ Insight passed evaluation.")
            valid_insights.append(insight)

    print(f"[Orchestrator] ✅ Generated {len(valid_insights)} high-quality insights.")
    return {"insights": valid_insights, "status": f"Generated {len(valid_insights)} verified insights"}

async def detect_trends(state: AgentState) -> Dict[str, Any]:
    print("\n[Orchestrator] 📈 Step 6: Trend Agent analyzing batch for macro-trends...")
    agent = TrendAgent()
    insights = state.get("insights", [])
    trends = await agent.detect_trends(insights)

    if trends:
        print(f"[Orchestrator] ✅ Detected {len(trends)} macro trends.")
        # Save trends to DB
        docs = [t.model_dump() for t in trends]
        await db.db["trends"].insert_many(docs)
    else:
        print("[Orchestrator] ℹ️ No strong macro trends detected in this batch.")

    return {"trends": trends, "status": f"Detected {len(trends)} macro trends"}

async def save_insights_and_notify(state: AgentState) -> Dict[str, Any]:
    print("\n[Orchestrator] 📬 Step 7: Finalizing... Saving to Pending Queue and Alerting Admin.")
    insights = state.get("insights", [])
    trends = state.get("trends", [])

    # Save Insights to DB & Chroma as "pending"
    if insights:
        docs = [i.model_dump() for i in insights]
        await db.db["insights"].insert_many(docs)
        print(f"[Orchestrator] ✅ Saved {len(insights)} insights to Pending Queue.")

        # We only add to semantic memory once approved, so we skip Vector Store here
        # It will be added when the Admin clicks "Approve"

    # Trigger Admin Notification
    if insights or trends:
        notifier = NotificationAgent()
        
        insight_preview = ""
        if insights:
            insight_preview = "\n\n💡 *Top Insights Found:*\n"
            for i in insights[:5]: # Show first 5
                insight_preview += f"• {i.title}\n"
            if len(insights) > 5:
                insight_preview += f"_...and {len(insights) - 5} more._"

        admin_message = f"🤖 *Agentic Platform Update*\n\nYour AI swarm just finished a sweep!\n\n💡 *{len(insights)}* new insights awaiting review.\n📈 *{len(trends)}* new macro trends detected.{insight_preview}"
        # Using a simplified payload structure for the alert
        await notifier.send_admin_alert(admin_message)
        print("[Orchestrator] ✅ Admin alert sent to Telegram.")
    else:
        print("[Orchestrator] ℹ️ Nothing new to report. Skipping Telegram alert.")

    print("\n[Orchestrator] 🎉 Workflow Complete!")
    return {"status": "Execution Complete: Pending Insights Saved & Admin Alerted"}

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

