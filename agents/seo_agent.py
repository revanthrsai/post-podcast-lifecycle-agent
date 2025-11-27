from google.adk import Agent
from config import Config
from tools.custom_tools import save_to_file
import json

def build_seo_agent():
    return Agent(
        name="SEOAgent",
        model=Config.MODEL_NAME,
        instruction="""
You generate SEO metadata for the final podcast.

You MUST return ONLY valid JSON with this structure:
{
  "title": "Short SEO-friendly title (<= 60 chars)",
  "meta_description": "Clean description (150-160 chars)",
  "keywords": ["keyword1", "keyword2", ..., "keyword20"]
}

DO NOT return text outside JSON.

After producing JSON:
Call the tool save_to_file(filename: str, content: str)
with:
{
  "filename": "seo.json",
  "content": "<the SAME JSON you produced>"
}

The final reply after tool call must be ONLY:
{"status": "saved"}
        """,
        tools=[save_to_file]
    )
