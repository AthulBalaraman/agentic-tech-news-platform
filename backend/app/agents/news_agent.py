import httpx
from ..core.config import get_settings
from ..models.raw_data import RawData
from datetime import datetime, timedelta

settings = get_settings()

class NewsAgent:
    def __init__(self):
        self.api_key = settings.NEWSAPI_KEY
        self.url = "https://newsapi.org/v2/everything"
        # Expanded queries based on user interest
        self.queries = [
            '"AI code editors" OR "Claude" OR "new LLMs"',
            '"prompt engineering" OR "AI system design" OR "FAANG AI"',
            '"AI architecture" OR "latest AI tools" OR "anti gravity"'
        ]

    async def fetch_news(self):
        """Fetch news from multiple AI topics and return the top 12 results."""
        all_articles = []
        seen_urls = set()
        
        # Look back 3 days for fresh news
        from_date = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")

        async with httpx.AsyncClient() as client:
            for query in self.queries:
                print(f"  -> Searching NewsAPI for: {query}...")
                params = {
                    "q": query,
                    "apiKey": self.api_key,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "from": from_date,
                    "pageSize": 10
                }
                
                try:
                    response = await client.get(self.url, params=params, timeout=15.0)
                    data = response.json()
                    
                    if data.get("status") != "ok":
                        print(f"⚠️ Error fetching from NewsAPI for query '{query}': {data}")
                        continue

                    for article in data.get("articles", []):
                        url = article.get("url")
                        # Basic deduplication
                        if not url or url in seen_urls:
                            continue
                        seen_urls.add(url)
                        
                        all_articles.append(RawData(
                            source="news",
                            external_id=url,
                            title=article.get("title", "Untitled"),
                            content=article.get("content") or article.get("description") or "",
                            metadata={
                                "author": article.get("author", "Unknown"),
                                "published_at": article.get("publishedAt", ""),
                                "source_name": article.get("source", {}).get("name", "NewsAPI"),
                                "description": article.get("description", ""),
                                "image_url": article.get("urlToImage", ""),
                                "search_query": query
                            }
                        ))
                except Exception as e:
                    print(f"❌ NewsAPI error for '{query}': {e}")
        
        # Sort all aggregated articles by published date descending
        all_articles.sort(key=lambda x: x.metadata.get("published_at", ""), reverse=True)
        
        # Return max 12 items to leave room for GitHub repos (Total limit ~15)
        return all_articles[:12]
