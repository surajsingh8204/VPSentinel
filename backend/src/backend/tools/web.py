import json

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from backend.config import settings


tavily_search = TavilySearch(
    max_results=5,
    tavily_api_key=settings.tavily_api_key,
)


@tool
def web_search(query: str) -> str:
    """Search the web for technical information, documentation, error messages, and DevOps troubleshooting information."""

    if not query.strip():
        return json.dumps({
            "error": "Search query cannot be empty."
        })

    try:
        results = tavily_search.invoke({
            "query": query,
        })

        return json.dumps(
            results,
            ensure_ascii=False,
            default=str,
        )

    except Exception as exc:
        return json.dumps({
            "error": str(exc),
        })