import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
try:
    from .config import ELEVENLABS_API_KEY
except ImportError:  # pragma: no cover
    from config import ELEVENLABS_API_KEY

# Initialize ElevenLabs client once at module load
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(text: str, folder: str) -> str:
    """Generate speech audio from text using ElevenLabs and save to audio.mp3 in the folder."""
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    # uncomment the line below to play the audio back
    # play(response)

    # Generating a unique file name for the output MP3 file
    save_file_path = os.path.join("user_uploads", folder, "audio.mp3")

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"Audio file generated: {save_file_path}")

    # Return the path of the saved audio file
    return save_file_path

