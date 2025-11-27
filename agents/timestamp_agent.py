from google.adk import Agent
from config import Config
from tools.custom_tools import save_to_file

def build_timestamp_agent():
    return Agent(
        name="TimestampAgent",
        model=Config.MODEL_NAME,
        instruction="""
You generate clean, human-friendly chapter timestamps for the podcast.

You MUST return ONLY valid JSON with this structure:

{
  "chapters": [
    {
      "start": "00:00",
      "title": "Introduction to topic"
    },
    {
      "start": "02:15",
      "title": "Main concept explained"
    },
    ...
  ]
}

RULES:
- You MUST ONLY output JSON.
- No .txt file creation.
- No extra commentary.
- No text outside JSON.

After producing JSON:
You MUST call save_to_file with:
{
  "filename": "timestamps.json",
  "content": "<the SAME JSON you produced>"
}

Finally, the assistant MUST return:
{"status": "saved"}
        """,
        tools=[save_to_file]
    )
