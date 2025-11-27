from google.adk import Agent
from config import Config

def build_outline_agent():
    return Agent(
        name="OutlineAgent",
        model=Config.MODEL_NAME,
        instruction="""
You are an outline generator.
Input context contains transcript and research.
Return ONLY JSON structured as:
{
  "hook": "<one-line hook>",
  "segments": [
    {"title":"Topic 1", "summary":"..."},
    ...
  ],
  "closing": "<one-line closing>"
}
Return exactly JSON only.
        """
    )
