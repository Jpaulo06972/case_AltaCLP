import os
from groq import Groq

# Default model definitions
DEFAULT_TEXT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_AUDIO_MODEL = "whisper-large-v3"

def get_groq_client():
    """
    Returns a configured Groq client instance.
    The GROQ_API_KEY environment variable must be set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[WARNING] GROQ_API_KEY not found in environment variables.")
        return None
        
    return Groq(api_key=api_key)
