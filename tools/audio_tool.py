import time
from typing import Dict
from google.genai import Client, types
from config import Config
from .adk_tool_wrappers import success, failure

def transcribe_audio(filepath: str, poll_interval: float = 2.0, timeout: int = 300) -> dict:
    """
    Upload audio file and request a verbatim transcript via GenAI.
    Explicit signature: filepath (string).
    Returns ToolResult-style dict from adk_tool_wrappers.
    """
    if not Config.API_KEY:
        return failure("GOOGLE_API_KEY not set in environment.")

    try:
        client = Client(api_key=Config.API_KEY)
    except Exception as e:
        return failure(f"Failed to create GenAI client: {e}")

    # Upload file
    try:
        file_ref = client.files.upload(file=filepath)
    except Exception as e:
        return failure(f"Error uploading file: {e}")

    start = time.time()
    while True:
        try:
            file_ref = client.files.get(name=file_ref.name)
        except Exception as e:
            return failure(f"Error polling file status: {e}")

        state = getattr(file_ref.state, "name", str(file_ref.state)).upper()
        if state == "ACTIVE":
            break
        if state == "FAILED":
            return failure("Audio processing failed on provider side.")
        if time.time() - start > timeout:
            return failure("Timeout waiting for audio processing.")
        time.sleep(poll_interval)

    # transcript generation
    try:
        response = client.models.generate_content(
            model=Config.MODEL_NAME,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(file_data=types.FileData(
                            mime_type=file_ref.mime_type,
                            file_uri=file_ref.uri
                        )),
                        types.Part(text=(
                            "Please generate a verbatim transcript of the provided audio file. "
                            "Return only the transcript text in the response."
                        ))
                    ]
                )
            ],
        )
    except Exception as e:
        return failure(f"Error generating transcript: {e}")

    # Extract transcript text
    text = getattr(response, "text", None)
    if not text:
        try:
            text = ""
            if getattr(response, "content", None):
                for c in response.content:
                    if getattr(c, "parts", None):
                        for p in c.parts:
                            if getattr(p, "text", None):
                                text += p.text
        except Exception:
            pass

    if not text:
        return failure("No transcript text returned from model.")

    return success({"transcript": text}, meta={"source_uri": getattr(file_ref, "uri", "")})
