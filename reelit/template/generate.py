import os
from texttoaudio import text_to_speech_file
import time
import subprocess

def texttoaudio(folder: str) -> None:
    print("Generating audio for folder:", folder)
    description_path = os.path.join("user_uploads", folder, "description.txt")
    if not os.path.exists(description_path):
        print(f"Error: description.txt not found in folder {folder}")
        return
    with open(description_path, "r", encoding="utf-8") as f:
        text = f.read()
    print(text, folder)
    try:
        text_to_speech_file(text, folder)
    except Exception as e:
        print("TTS failed, using fallback audio:", e)
        # fallback: copy a sample track if available
        songs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'songs')
        fallback = None
        for name in ['1.mp3', '2.mp3', '3.mp3']:
            candidate = os.path.join(songs_dir, name)
            if os.path.exists(candidate):
                fallback = candidate
                break
        if fallback:
            dst = os.path.join("user_uploads", folder, "audio.mp3")
            with open(fallback, 'rb') as src, open(dst, 'wb') as out:
                out.write(src.read())
        else:
            raise
    input_path = os.path.join("user_uploads", folder, "input.txt")
    if not os.path.exists(input_path):
        print(f"Error: input.txt not found in folder {folder}")
        return

def create_reel(folder: str) -> None:
    # Resolve to Flask static folder location relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    reels_dir = os.path.join(static_dir, "reels")
    os.makedirs(reels_dir, exist_ok=True)
    input_txt = os.path.join("user_uploads", folder, "input.txt")
    audio_mp3 = os.path.join("user_uploads", folder, "audio.mp3")
    output_mp4 = os.path.join(reels_dir, f"{folder}.mp4")

    # Use double quotes around paths to be Windows-safe (spaces etc.)
    command = (
        f"ffmpeg -f concat -safe 0 -i \"{input_txt}\" -i \"{audio_mp3}\" "
        f"-vf \"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black\" "
        f"-c:v libx264 -c:a aac -shortest -pix_fmt yuv420p \"{output_mp4}\""
    )
    try:
        subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        print(f"Reel created successfully for folder: {folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating reel for folder {folder}: {e.stderr.decode()}")

if __name__ == "__main__":
    while True:
        print("Checking for new folders...")
        # Check if done.txt exists
        if not os.path.exists("done.txt"):
            # Create an empty done.txt if it doesn't exist
            with open("done.txt", "w") as f:
                pass
            
        # Read the contents of done.txt
        with open("done.txt", "r") as f:
            done_folders = f.readlines()

        done_folders = [line.strip() for line in done_folders]

        folders = os.listdir("user_uploads")
        for folder in folders:
            if folder not in done_folders:
                texttoaudio(folder)
                create_reel(folder)
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")
        time.sleep(3)