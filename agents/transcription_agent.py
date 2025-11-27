from google.adk import Agent
from config import Config
from tools.audio_tool import transcribe_audio

def build_transcription_agent():
    return Agent(
        name="TranscriptionAgent",
        model=Config.MODEL_NAME,
        instruction="""
You are a transcription agent.
You MUST invoke the function 'transcribe_audio' with a single parameter:
  filepath (string) - local path to the audio file.

After the tool returns, produce ONLY JSON of the form:
{
  "transcript": "<full transcript text>",
  "word_count": <int>
}
No commentary, no markdown.
        """,
        tools=[transcribe_audio]
    )
