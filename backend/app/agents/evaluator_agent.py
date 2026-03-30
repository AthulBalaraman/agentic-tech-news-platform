import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from ..models.raw_data import RawData
from ..models.insight import Insight
from ..core.config import get_settings

settings = get_settings()

class EvaluatorAgent:
    def __init__(self):
        # Using Gemini 1.5 Pro for critical evaluation and complex reasoning
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.1,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.prompt = PromptTemplate.from_template(
            """You are a strict Quality Control AI. Review the generated technical insight against the original raw content.
            
            Original Title: {title}
            Original Content: {content}
            
            Generated Insight:
            What it is: {what_is_it}
            Why it matters: {why_it_matters}
            Technical implementation: {technical_implementation}
            
            Evaluate for:
            1. Accuracy (No hallucinations - everything must be grounded in the text)
            2. Conciseness (No fluff)
            3. Technical depth (Must sound like an experienced engineer)
            
            Respond ONLY in valid JSON:
            {{
                "score": <int 0-100>,
                "feedback": "<string: specific instructions on what to fix if score < 70, otherwise 'Looks good'>"
            }}
            """
        )

    async def evaluate(self, raw_data: RawData, insight: Insight) -> dict:
        chain = self.prompt | self.llm
        try:
            content_snippet = raw_data.content[:4000]
            response = await chain.ainvoke({
                "title": raw_data.title,
                "content": content_snippet,
                "what_is_it": insight.what_is_it,
                "why_it_matters": insight.why_it_matters,
                "technical_implementation": insight.technical_implementation
            })
            
            raw_json = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_json)
        except Exception as e:
            print(f"⚠️ Evaluator failed for {insight.title}: {e}")
            return {"score": 0, "feedback": "Evaluation pipeline failed."}
