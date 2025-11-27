from google.adk import Agent
from config import Config
from tools.search_tool import web_search

def build_research_agent():
    return Agent(
        name="ResearchAgent",
        model=Config.MODEL_NAME,
        instruction="""
You are an expert researcher.
Call the tool 'web_search' with:
  - query (string)
  - num_results (integer, default 3)
Return ONLY JSON with:
{
  "summary": "<3-5 sentence summary>",
  "bullets": ["key fact 1", "key fact 2"],
  "citations": [{"title":"...", "url":"...", "snippet":"..."}]
}
Do not include extra commentary.
        """,
        tools=[web_search]
    )
