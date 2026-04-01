import httpx
from ..core.config import get_settings
from ..models.raw_data import RawData

settings = get_settings()

class NewsAgent:
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.url = "https://newsapi.org/v2/everything"

    async def fetch_news(self, query: str = "agentic ai frameworks"):
        params = {
            "q": query,
            "apiKey": self.api_key,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 10
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url, params=params)
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"Error fetching from NewsAPI: {data}")
                return []

            results = []
            for article in data.get("articles", []):
                results.append(RawData(
                    source="news",
                    external_id=article["url"],
                    title=article["title"],
                    content=article["content"] or article["description"] or "",
                    metadata={
                        "author": article["author"],
                        "published_at": article["publishedAt"],
                        "source_name": article["source"]["name"],
                        "description": article["description"],
                        "image_url": article.get("urlToImage", "")
                    }
                ))
            return results
