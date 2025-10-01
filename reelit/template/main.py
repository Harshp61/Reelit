from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os
from generate import texttoaudio, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = str(uuid.uuid1())
    if request.method == "POST":
        rec_id = request.form.get("myid")
        desc = request.form.get("text")
        input_files = []
        if not rec_id:
            rec_id = myid  # Fallback to generated ID if not provided
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        for key, value in request.files.items():
            file = request.files[key]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_path, filename))
                input_files.append(filename)

        # Write description once per request
        with open(os.path.join(upload_path, "description.txt"), "w", encoding="utf-8") as f:
            f.write(desc if desc else "No description provided.")

        # Build ffmpeg concat file with Windows-safe quoting
        input_txt_path = os.path.join(upload_path, "input.txt")
        # Overwrite if exists to avoid stale entries
        with open(input_txt_path, "w", encoding="utf-8") as f:
            # Add ffconcat header for robustness
            f.write("ffconcat version 1.0\n")
            for fl in input_files:
                img_path = os.path.join(upload_path, fl)
                # Use absolute path and escape backslashes by using forward slashes
                abs_img_path = os.path.abspath(img_path).replace('\\', '/')
                f.write(f"file '{abs_img_path}'\n")
                f.write("duration 3\n")

        # Trigger audio and reel generation synchronously
        try:
            if not input_files:
                print("No valid image files were uploaded; skipping generation.")
            else:
                texttoaudio(rec_id)
                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'audio.mp3')
                if not os.path.exists(audio_path):
                    print("Audio generation failed: audio.mp3 not found at", audio_path)
                create_reel(rec_id)
                reels_dir = os.path.join(app.static_folder, "reels")
                output_file = os.path.join(reels_dir, f"{rec_id}.mp4")
                if not os.path.exists(output_file):
                    print("Reel generation failed: output not found at", output_file)
        except Exception as e:
            print("Error generating audio/reel:", e)
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels_dir = os.path.join(app.static_folder, "reels")
    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir, exist_ok=True)
    reels = [f for f in os.listdir(reels_dir) if f.lower().endswith('.mp4')]
    reels.sort(reverse=True)
    return render_template("gallery.html", reels=reels)

if __name__ == "__main__":
    app.run(debug=True)