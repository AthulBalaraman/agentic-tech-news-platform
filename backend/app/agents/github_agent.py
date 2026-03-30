import httpx
from ..core.config import get_settings
from ..models.raw_data import RawData
from datetime import datetime

settings = get_settings()

class GitHubAgent:
    def __init__(self):
        self.url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"bearer {settings.GITHUB_TOKEN}"}

    async def fetch_trending_repos(self, query: str = "mcp server"):
        # Basic GraphQL query to search for repositories
        gql_query = """
        query($searchQuery: String!) {
          search(query: $searchQuery, type: REPOSITORY, first: 10) {
            edges {
              node {
                ... on Repository {
                  nameWithOwner
                  url
                  description
                  stargazerCount
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
        variables = {"searchQuery": f"{query} sort:updated-desc"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                json={"query": gql_query, "variables": variables},
                headers=self.headers
            )
            data = response.json()
            
            if "data" not in data or "search" not in data["data"]:
                print(f"Error fetching from GitHub: {data}")
                return []

            results = []
            for edge in data["data"]["search"]["edges"]:
                repo = edge["node"]
                results.append(RawData(
                    source="github",
                    external_id=repo["url"],
                    title=repo["nameWithOwner"],
                    content=repo.get("readme", {}).get("text", repo["description"] or ""),
                    metadata={
                        "stars": repo["stargazerCount"],
                        "updated_at": repo["updatedAt"],
                        "description": repo["description"]
                    }
                ))
            return results
