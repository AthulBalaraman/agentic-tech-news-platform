import httpx
from ..core.config import get_settings
from ..models.raw_data import RawData
from datetime import datetime, timedelta

settings = get_settings()

class GitHubAgent:
    def __init__(self):
        self.url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"Bearer {settings.GITHUB_TOKEN}"}
        # Defined topics to track
        self.target_topics = [
            "mcp server",
            "ai agent framework",
            "langgraph",
            "autogen",
            "rag pipeline",
            "context engineering"
        ]

    async def fetch_trending_repos(self):
        """Fetch high-quality repositories across multiple AI topics."""
        all_results = []
        # Calculate date for 'recently updated' (e.g., last 14 days for higher quality)
        since_date = (datetime.utcnow() - timedelta(days=14)).strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            for topic in self.target_topics:
                print(f"  -> Searching GitHub for: {topic}...")
                
                # Higher star threshold for "top performing" repos
                search_query = f"{topic} stars:>200 pushed:>{since_date} sort:stars-desc"
                
                gql_query = """
                query($searchQuery: String!) {
                  search(query: $searchQuery, type: REPOSITORY, first: 5) {
                    edges {
                      node {
                        ... on Repository {
                          nameWithOwner
                          url
                          description
                          stargazerCount
                          forkCount
                          updatedAt
                          readme: object(expression: "HEAD:README.md") {
                            ... on Blob {
                              text
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """
                variables = {"searchQuery": search_query}

                try:
                    response = await client.post(
                        self.url,
                        json={"query": gql_query, "variables": variables},
                        headers=self.headers,
                        timeout=25.0
                    )
                    data = response.json()

                    if "data" not in data or "search" not in data["data"]:
                        print(f"⚠️ Error fetching {topic} from GitHub: {data.get('errors')}")
                        continue

                    for edge in data["data"]["search"]["edges"]:
                        repo = edge["node"]
                        
                        # Use README if available, else description
                        readme_obj = repo.get("readme")
                        content = repo.get("description") or ""
                        if readme_obj and isinstance(readme_obj, dict):
                            content = readme_obj.get("text", content)

                        all_results.append(RawData(
                            source="github",
                            external_id=repo["url"],
                            title=repo["nameWithOwner"],
                            content=content,
                            metadata={
                                "stars": repo.get("stargazerCount", 0),
                                "forks": repo.get("forkCount", 0),
                                "updated_at": repo.get("updatedAt", ""),
                                "description": repo.get("description", ""),
                                "search_topic": topic
                            }
                        ))
                except Exception as e:
                    print(f"❌ GitHub API error for {topic}: {e}")
        
        return all_results



