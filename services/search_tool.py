import os

# LangChain Tool abstraction (used by agent to call external functions)
from langchain.agents import Tool

# SerpAPI client for Google Search
from serpapi import GoogleSearch


def serpapi_search(query: str) -> str:
    """
    Perform a Google search using SerpAPI and return a short snippet.

    This tool is used by the agent to retrieve real-time or external information
    that is not available in the local knowledge base (e.g. PDF documents).
    """
    params = {
        "engine": "google",  # Search engine type
        "q": query,          # Search query
        "api_key": os.getenv("SERPAPI_API_KEY"),  # API key from environment variables
    }

    # Execute search request
    search = GoogleSearch(params)
    results = search.get_dict()

    # Extract the first organic search result snippet (if available)
    if "organic_results" in results and len(results["organic_results"]) > 0:
        return results["organic_results"][0].get("snippet", "No snippet found.")

    # Fallback if no results found
    return "No relevant results found."


# Define LangChain Tool wrapper
search_tool = Tool(
    name="Google Search",
    func=serpapi_search,
    description="Useful for answering questions about current events or external information not contained in local documents."
)