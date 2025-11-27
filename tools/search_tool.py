import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .adk_tool_wrappers import success, failure

def web_search(query: str, num_results: int = 3, recency_days: Optional[int] = None) -> dict:
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": "podcast-lifecycle-agent/1.0 (+https://example.local)"}
        resp = requests.post(url, data=params, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results: List[Dict[str, str]] = []
        for r in soup.find_all("div", {"class": "result__body"}, limit=num_results):
            title_tag = r.find("a", {"class": "result__a"})
            snippet_tag = r.find("a", {"class": "result__snippet"}) or r.find("div", {"class": "result__snippet"})
            href = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
            title = title_tag.get_text(strip=True) if title_tag else ""
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            results.append({"title": title, "url": href, "snippet": snippet})

        if not results:
            return failure("No search results found.")
        return success(results, meta={"query": query, "num_results": len(results)})
    except Exception as e:
        return failure(f"Search failed: {e}")
