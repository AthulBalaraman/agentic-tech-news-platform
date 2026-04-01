import json
import re
import httpx
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from ..models.raw_data import RawData
from ..models.insight import Insight
from ..core.config import get_settings

settings = get_settings()

class SummarizerAgent:
    def __init__(self):
        # We switch to Gemini 1.5 Pro here because it handles multi-modal (Vision) tasks much better
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,
            google_api_key=settings.GEMINI_API_KEY
        )
        
        self.system_prompt = """You are an expert AI technical analyst tracking developments in Model Context Protocol (MCP), RAG, and Agentic Frameworks. 
            Analyze the following text content AND any provided architecture diagrams/images to extract a structured technical insight.

            {feedback_section}

            Respond ONLY in valid JSON format matching this schema:
            {{
                "what_is_it": "A concise 1-sentence summary of what this tool or framework does.",
                "why_it_matters": "A 1-2 sentence explanation of its impact on the AI ecosystem.",
                "technical_implementation": "A detailed, in-depth explanation (2-3 paragraphs) of its underlying tech, architecture, and how a developer would use it. Be thorough and comprehensive.",
                "tags": ["tag1", "tag2", "tag3"]
            }}
            """

    def _extract_image_urls(self, text: str) -> list[str]:
        # Basic markdown image extraction ![alt text](image_url)
        # Filters for common architecture diagram extensions
        urls = re.findall(r'!\[.*?\]\((.*?)\)', text)
        return [url for url in urls if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp'])]

    async def _download_image_as_base64(self, url: str) -> str | None:
        try:
            # Handle relative github paths if necessary (Simplified for MVP)
            if url.startswith('/'):
                return None 
                
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            print(f"⚠️ Failed to download image {url}: {e}")
        return None

    async def summarize(self, item: RawData, feedback: str = None) -> Insight | None:
        try:
            content_snippet = item.content[:4000]
            feedback_section = f"CRITICAL FEEDBACK FROM EVALUATOR (Must fix): {feedback}" if feedback else ""
            
            # Construct the textual prompt
            prompt_text = self.system_prompt.format(feedback_section=feedback_section)
            prompt_text += f"\n\nContent Title: {item.title}\nContent Source: {item.source}\nContent: {content_snippet}"
            
            # Prepare Multi-Modal Message Payload
            message_content = [{"type": "text", "text": prompt_text}]
            
            # Look for architecture diagrams to enhance the analysis
            image_urls = self._extract_image_urls(item.content)
            if image_urls:
                # Just take the first image for token efficiency (usually the main architecture diagram in a README)
                base64_img = await self._download_image_as_base64(image_urls[0])
                if base64_img:
                    print(f"👁️ Vision Agent analyzing architecture diagram for {item.title}")
                    message_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                    })

            # Execute Gemini Pro Vision Call
            response = await self.llm.ainvoke([HumanMessage(content=message_content)])
            
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
                tags=parsed.get("tags", []),
                metadata=item.metadata
            )
        except Exception as e:
            print(f"⚠️ Summarizer failed for {item.title}: {e}")
            return None
