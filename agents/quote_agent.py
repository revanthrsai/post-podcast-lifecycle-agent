from google.adk import Agent
from config import Config
from tools.custom_tools import save_to_file

def build_quote_agent():
    return Agent(
        name="QuoteAgent",
        model=Config.MODEL_NAME,
        instruction="""
Extract exactly 5 punchy quotes under 280 chars each.
Return JSON:
{"quotes":["q1","q2","q3","q4","q5"]}
Then call save_to_file(filename: str, content: str) with filename="quotes.md"
and content formatted as a numbered list.
Finally reply only with: {"status":"saved"}
        """,
        tools=[save_to_file]
    )
