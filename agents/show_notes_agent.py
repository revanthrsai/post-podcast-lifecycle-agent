from google.adk import Agent
from config import Config
from tools.custom_tools import save_to_file

def build_show_notes_agent():
    return Agent(
        name="ShowNotesAgent",
        model=Config.MODEL_NAME,
        instruction="""
You generate podcast show notes in JSON format ONLY.

The required JSON structure is:

{
  "summary": "A clear summary of the episode (200-400 words)",
  "bullets": [
    "insight 1",
    "insight 2",
    "insight 3",
    ...
  ]
}

RULES:
- You MUST return ONLY valid JSON.
- No markdown.
- No plain text.
- No extra commentary.
- Do NOT create .md files.
- After generating the JSON, you MUST call save_to_file with:
  {
    "filename": "show_notes.json",
    "content": "<the SAME JSON you produced>"
  }

Your final assistant message MUST be:
{"status": "saved"}
        """,
        tools=[save_to_file]
    )
