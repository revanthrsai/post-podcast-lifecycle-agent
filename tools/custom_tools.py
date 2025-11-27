import os
import json
from typing import Any
from .adk_tool_wrappers import success, failure

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save content to outputs/
def save_to_file(filename: str, content: str) -> dict:
    try:
        if not filename or not isinstance(filename, str):
            return failure("Invalid filename argument.")

        path = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content or "")

        return success({"path": path}, meta={"filename": filename})
    except Exception as e:
        return failure(f"Error saving file: {e}")

# Read transcript file and return text
def read_transcript(filepath: str) -> str:

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading transcript: {e}"
