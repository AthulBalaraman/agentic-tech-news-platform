import httpx
from ..core.config import get_settings
from ..models.raw_data import RawData
from datetime import datetime

settings = get_settings()

class GitHubAgent:
    def __init__(self):
        self.url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"Bearer {settings.GITHUB_TOKEN}"}

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

                # Safely handle missing READMEs
                readme_obj = repo.get("readme")
                content = repo.get("description") or ""
                if readme_obj and isinstance(readme_obj, dict):
                    content = readme_obj.get("text", content)

                results.append(RawData(
                    source="github",
                    external_id=repo["url"],
                    title=repo["nameWithOwner"],
                    content=content,
                    metadata={
                        "stars": repo.get("stargazerCount", 0),
                        "updated_at": repo.get("updatedAt", ""),
                        "description": repo.get("description", "")
                    }
                ))
            return results



