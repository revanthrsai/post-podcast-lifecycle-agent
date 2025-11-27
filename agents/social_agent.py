from google.adk import Agent
from config import Config
from tools.custom_tools import save_to_file

def build_social_agent():
    return Agent(
        name="SocialMediaAgent",
        model=Config.MODEL_NAME,
        instruction="""
You generate social media content in STRICT JSON format.

Your output MUST follow this exact structure:

{
  "twitter_thread": [
    "1. <tweet 1>",
    "2. <tweet 2>",
    "3. <tweet 3>"
  ],
  "linkedin_posts": [
    "<LinkedIn post 1>",
    "<LinkedIn post 2>"
  ],
  "instagram_captions": [
    "<Instagram caption 1>",
    "<Instagram caption 2>"
  ]
}

### HARD RULES
- YOU MUST output ONLY valid JSON.
- DO NOT write markdown.
- DO NOT write plain text.
- DO NOT output '/n'.
- DO NOT output '1/n', '2/n', or any thread style using slash.
- Twitter threads MUST use simple numbering: "1.", "2.", "3.".
- Each tweet MUST be its own list entry (no newlines).
- LinkedIn posts must be 2–4 sentences each.
- Instagram captions must include emojis and 3–6 hashtags.

### TOOL CALL REQUIREMENT
After generating the JSON, you MUST call save_to_file with:

{
  "filename": "social.json",
  "content": "<the EXACT SAME JSON you produced>"
}

Finally, as your last assistant message, reply ONLY with:
{"status": "saved"}

NO extra text. NO explanations. NO markdown.
""",
        tools=[save_to_file]
    )
