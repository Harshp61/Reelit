import os

# Read from environment at runtime; leave empty string if not provided
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
