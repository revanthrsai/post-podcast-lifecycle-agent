import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Credentials
    API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "")
    LOCATION: str = os.getenv("GOOGLE_LOCATION", "asia-south1")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.0-flash")

    # Required Folders
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
    AUDIO_DIR = os.path.join(ROOT_DIR, "podcast_recordings")
    TESTDATA_DIR = os.path.join(ROOT_DIR, "test_data")

    @staticmethod
    def init_directories():
        """Ensure essential folders exist."""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.AUDIO_DIR, exist_ok=True)
        os.makedirs(Config.TESTDATA_DIR, exist_ok=True)

# Initialize dirs if not present
Config.init_directories()
