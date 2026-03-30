import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from ..models.raw_data import RawData
from ..models.insight import Insight
from ..core.config import get_settings

settings = get_settings()

class SummarizerAgent:
    def __init__(self):
        # Using Gemini 1.5 Flash for rapid text synthesis
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY
        )
        
        self.prompt = PromptTemplate.from_template(
            """You are an expert AI technical analyst tracking developments in Model Context Protocol (MCP), RAG, and Agentic Frameworks. 
            Analyze the following content and extract a structured technical insight.

            Content Title: {title}
            Content Source: {source}
            Content: {content}

            {feedback_section}

            Respond ONLY in valid JSON format matching this schema:
            {{
                "what_is_it": "A concise 1-sentence summary of what this tool or framework does.",
                "why_it_matters": "A 1-2 sentence explanation of its impact on the AI ecosystem.",
                "technical_implementation": "A brief explanation of its underlying tech or how a developer would use it.",
                "tags": ["tag1", "tag2", "tag3"]
            }}
            """
        )

    async def summarize(self, item: RawData, feedback: str = None) -> Insight | None:
        chain = self.prompt | self.llm
        try:
            # We send only the first 4000 chars to save tokens if content is a huge README
            content_snippet = item.content[:4000]
            
            feedback_section = ""
            if feedback:
                feedback_section = f"CRITICAL FEEDBACK FROM EVALUATOR (Must fix): {feedback}"
            
            response = await chain.ainvoke({
                "title": item.title,
                "source": item.source,
                "content": content_snippet,
                "feedback_section": feedback_section
            })
            
            # Clean formatting in case Gemini returns markdown blocks
            raw_json = response.content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw_json)
            
            return Insight(
                title=item.title,
                source=item.source,
                external_id=item.external_id,
                what_is_it=parsed.get("what_is_it", "N/A"),
                why_it_matters=parsed.get("why_it_matters", "N/A"),
                technical_implementation=parsed.get("technical_implementation", "N/A"),
                tags=parsed.get("tags", [])
            )
        except Exception as e:
            print(f"⚠️ Summarizer failed for {item.title}: {e}")
            return None
