<div align="center">

# ReelIt — AI Reel Generator

Turn your images and text into vertical reels with auto-generated voiceovers using ElevenLabs and ffmpeg.

</div>

---

## Features

- AI text-to-speech voiceover via ElevenLabs
- Image stitching into 1080x1920 vertical reels using ffmpeg
- Immediate reel generation on upload (no background worker required)
- Light/Dark mode toggle with localStorage persistence
- Colorful, modern, glassy 3D UI
- Simple gallery to preview generated reels

## Tech Stack

- Python, Flask
- ElevenLabs TTS
- ffmpeg (CLI)
- HTML, Jinja, Bootstrap, custom CSS

## Demo (Local)

- Create: upload multiple images and enter text → generates `audio.mp3` and `static/reels/<id>.mp4`
- Gallery: lists all files in `static/reels` and lets you play them

## Project Structure

```
reelit/
  template/
    main.py             # Flask app (routes and upload handling)
    generate.py         # Text→audio + ffmpeg reel creation
    texttoaudio.py      # ElevenLabs TTS client wrapper
    config.py           # ELEVENLABS_API_KEY (you add your key here)
    templates/          # Jinja templates (base, index, create, gallery)
    static/
      css/              # style.css, create.css, gallery.css
      songs/            # sample songs (optional)
      reels/            # output reels (created at runtime)
user_uploads/           # uploads and generated audio/input.txt per session
README.md
```

## Prerequisites

- Python 3.9+
- ffmpeg installed and available on PATH
  - Windows: install from `https://ffmpeg.org/` or Chocolatey: `choco install ffmpeg`
  - macOS: Homebrew: `brew install ffmpeg`
  - Linux: your package manager (e.g., `sudo apt install ffmpeg`)
- ElevenLabs API key (`https://elevenlabs.io/`)

## Setup

1) Clone the repo
```bash
git clone <your-repo-url>
cd reelit
```

2) Create and activate a virtual environment
```bash
# Windows (PowerShell)
python -m venv .venv
. .venv/Scripts/Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies
```bash
pip install flask elevenlabs
```

4) Configure ElevenLabs API key

Create or edit `reelit/template/config.py` to contain your key:
```python
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
```

5) Run the app
```bash
# From project root or from reelit/template directory
python reelit/template/main.py
# or
cd reelit/template && python main.py
```

The app runs at `http://127.0.0.1:5000/`.

## Usage

1) Go to Create page
   - Enter the text that should be converted to voice
   - Upload one or more images (`.png`, `.jpg`, `.jpeg`)
   - Submit to generate
2) The app will:
   - Save your images into `user_uploads/<id>/`
   - Save your text into `description.txt`
   - Generate `audio.mp3` using ElevenLabs
   - Build `input.txt` for ffmpeg and render the reel into `static/reels/<id>.mp4`
3) Check the Gallery page to play your reel(s)

## Configuration Notes

- Output folder: reels are written to `reelit/template/static/reels/`
- Uploads and working files: `user_uploads/<id>/` contains images, `description.txt`, `input.txt`, `audio.mp3`
- Allowed image types: `.png`, `.jpg`, `.jpeg`
- Duration per image: currently 3 seconds (see `main.py` where `input.txt` is written)
- Light/Dark mode: Toggle in navbar; preference saved in localStorage

## Troubleshooting

- ffmpeg not found
  - Ensure `ffmpeg` is installed and available on PATH (restart terminal after install)
- Audio not generated
  - Verify your `ELEVENLABS_API_KEY` is valid
  - Check console logs where `main.py` runs for any errors
- Reel not created
  - Confirm images were uploaded and `user_uploads/<id>/input.txt` exists
  - Check that `static/reels` directory exists (created automatically in code)

## Security

- Do not commit your real `ELEVENLABS_API_KEY` to source control.
- Consider using environment variables or a secrets manager in production.

## Roadmap Ideas

- Drag-and-drop uploads with previews
- Background job queue for long-running renders
- Per-image timing controls
- Music track selection and mixing
- Deployment templates (Docker, Railway, Fly.io)

## License

MIT

## Acknowledgements

- ElevenLabs for TTS
- ffmpeg for video composition
