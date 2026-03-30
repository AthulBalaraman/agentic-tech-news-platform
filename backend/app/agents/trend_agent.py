import json
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from ..models.insight import Insight
from ..models.trend import Trend
from ..core.config import get_settings

settings = get_settings()

class TrendAgent:
    def __init__(self):
        # Gemini 1.5 Flash is perfect for pattern recognition across multiple items
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.prompt = PromptTemplate.from_template(
            """You are an AI Tech Trend Analyst. Review the following recent technical insights and identify 1-3 macro trends.
            For example: "Rise of Postgres MCP Servers", "Agentic RAG frameworks gaining traction", or "Shift towards local embedding models".
            
            Recent Insights:
            {insights_text}
            
            Respond ONLY in valid JSON format matching this schema (a list of objects):
            [
                {{
                    "trend_name": "Name of the trend (e.g. Rise of LangGraph)",
                    "description": "Why this trend is happening and its broader impact on AI engineering.",
                    "related_insights": ["Title 1", "Title 2"]
                }}
            ]
            """
        )

    async def detect_trends(self, insights: List[Insight]) -> List[Trend]:
        if not insights or len(insights) < 3:
            return [] # Need a critical mass of data points to form a real trend
            
        insights_text = "\n\n".join([f"- {i.title}: {i.what_is_it}" for i in insights])
        chain = self.prompt | self.llm
        
        try:
            response = await chain.ainvoke({"insights_text": insights_text})
            raw_json = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_json)
            
            trends = []
            for t in parsed:
                trends.append(Trend(
                    trend_name=t.get("trend_name", "Unknown Trend"),
                    description=t.get("description", ""),
                    related_insights=t.get("related_insights", [])
                ))
            return trends
        except Exception as e:
            print(f"⚠️ Trend Agent failed: {e}")
            return []
