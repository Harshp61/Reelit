from flask import Flask, render_template, request, redirect, url_for, flash
import uuid
from werkzeug.utils import secure_filename
import os
try:
    # When imported as a package (Render/gunicorn)
    from .generate import texttoaudio, create_reel
except ImportError:  # pragma: no cover
    # When running the file directly (local dev)
    from generate import texttoaudio, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

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
                flash("No valid image files were uploaded.", "error")
            else:
                texttoaudio(rec_id)
                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id, 'audio.mp3')
                if not os.path.exists(audio_path):
                    flash("Audio generation failed.", "error")
                create_reel(rec_id)
                reels_dir = os.path.join(app.static_folder, "reels")
                output_file = os.path.join(reels_dir, f"{rec_id}.mp4")
                if not os.path.exists(output_file):
                    flash("Reel generation failed.", "error")
                else:
                    flash("Reel generated successfully!", "success")
                    return redirect(url_for('gallery'))
        except Exception as e:
            print("Error generating audio/reel:", e)
            flash("Unexpected error during generation.", "error")
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels_dir = os.path.join(app.static_folder, "reels")
    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir, exist_ok=True)
    reels = [f for f in os.listdir(reels_dir) if f.lower().endswith('.mp4')]
    reels.sort(reverse=True)
    return render_template("gallery.html", reels=reels)

@app.post("/delete-reel")
def delete_reel():
    reel_filename = request.form.get('reel')
    if not reel_filename or not reel_filename.lower().endswith('.mp4'):
        flash('Invalid reel specified.', 'error')
        return redirect(url_for('gallery'))

    reels_dir = os.path.join(app.static_folder, 'reels')
    reel_path = os.path.join(reels_dir, reel_filename)

    # Only allow deletion within the reels directory
    if not os.path.abspath(reel_path).startswith(os.path.abspath(reels_dir)):
        flash('Unauthorized path.', 'error')
        return redirect(url_for('gallery'))

    # Derive upload/session folder from UUID part of filename
    reel_id = os.path.splitext(reel_filename)[0]
    upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], reel_id)

    try:
        if os.path.exists(reel_path):
            os.remove(reel_path)
        # Best-effort cleanup of associated upload folder
        if os.path.isdir(upload_folder):
            # Remove files then folder
            for name in os.listdir(upload_folder):
                try:
                    os.remove(os.path.join(upload_folder, name))
                except Exception:
                    pass
            try:
                os.rmdir(upload_folder)
            except Exception:
                pass
        flash('Reel deleted successfully.', 'success')
    except Exception as e:
        print('Error deleting reel:', e)
        flash('Failed to delete reel.', 'error')
    return redirect(url_for('gallery'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)