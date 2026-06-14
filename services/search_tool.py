import os
from langchain.agents import Tool
from serpapi import GoogleSearch


def serpapi_search(query: str) -> str:
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" in results and len(results["organic_results"]) > 0:
        return results["organic_results"][0].get("snippet", "No snippet found.")

    return "No relevant results found."


search_tool = Tool(
    name="Google Search",
    func=serpapi_search,
    description="Useful for answering questions about current events."
)