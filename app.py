import os
from datetime import datetime
from io import BytesIO
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    current_user,
    logout_user,
)
from pymongo import MongoClient
from gridfs import GridFS
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from werkzeug.security import generate_password_hash, check_password_hash
from pydub import AudioSegment
import speech_recognition as sr

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET")

client = MongoClient(os.getenv("DB_URI"))
db = client["audio_db"]
grid_fs = GridFS(db)
metadata_collection = db["audio_metadata"]
users_collection = db["users"]

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"  

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles registration.
    """
    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        print("Username and password are required.", "error")
        return redirect(url_for("register"))

    if users_collection.find_one({"username": username}):
        print("Username already exists. Please choose a different one.", "error")
        return redirect(url_for("register"))

    password_hash = generate_password_hash(password)
    new_user = {"username": username, "password_hash": password_hash}

    try:
        users_collection.insert_one(new_user)
        print("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    except PyMongoError as e:
        print("Database error occurred. Please try again.", "error")
        return str(e), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles  login
    """
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        print("Username and password are required.", "error")
        return redirect(url_for("login"))

    user = users_collection.find_one({"username": username})
    if not user:
        print("Invalid username or password.", "error")
        return redirect(url_for("login"))

    if not check_password_hash(user["password_hash"], password):
        print("Invalid username or password.", "error")
        return redirect(url_for("login"))

    login_user(User(user["username"]))
    session["username"] = username
    print("Login successful.", "success")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """
    Handles logout
    """
    logout_user()
    session.pop("username", None)
    print("Logged out successfully.", "success")
    return redirect(url_for("login"))


class User(UserMixin):
    """
    User class
    """
    def __init__(self, username):
            self.id = username

    @staticmethod
    def from_db(username):
        """Load a User object from the database."""
        user_data = users_collection.find_one({"username": username})
        if user_data:
            return User(username=user_data["username"])
        return None

@login_manager.user_loader
def load_user(username):
    return User.from_db(username)

def fetch_and_convert_to_wav(file_id):
    grid_file = grid_fs.get(file_id)
    content_type = grid_file.content_type

    file_data = grid_file.read()
    audio = AudioSegment.from_file(
        BytesIO(file_data), format=content_type.split("/")[-1]
    )
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    return wav_io


def perform_speech_recognition(wav_io):
    """
    Perform speech-to-text on a WAV file.
    """
    recognizer = sr.Recognizer()

    print(f"Buffer size: {len(wav_io.getvalue())} bytes")
    try:
        print("Starting speech recognition...")

        with sr.AudioFile(wav_io) as source:
            print("Audio file opened successfully.")
            audio_data = recognizer.record(source)
            print("Audio data recorded successfully.")
            transcription = recognizer.recognize_sphinx(audio_data)
            print("Transcription completed successfully:", transcription)
            return transcription

    except sr.UnknownValueError:
        print("CMU Sphinx could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"CMU Sphinx request failed: {e}")
        return None
    except Exception as e:
        print("Error during speech recognition:")
        print(str(e))
        raise


def transcribe(file_id):
    """
    Predict transcription for the given file_id.
    """
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

    try:
        file_id = ObjectId(file_id)
        print("trying to fetch file")
        wav_io = fetch_and_convert_to_wav(file_id)
        print("file loaded and converted")
        transcription = perform_speech_recognition(wav_io)
        print("Transcription loaded:", transcription)

        result = metadata_collection.update_one(
            {"file_id": str(file_id)},
            {
                "$set": {
                    "transcription": transcription,
                    "processed_time": datetime.utcnow(),
                    "status": "completed",
                }
            },
        )

        if result.matched_count == 0:
            print("No document matched the query. Update failed.")
        elif result.modified_count == 0:
            print("Document matched, but no changes were made.")
        else:
            print("Document updated successfully.")
        return (
            jsonify(
                {
                    "message": "Prediction completed successfully",
                    "file_id": str(file_id),
                    "status": "completed",
                    "transcription": transcription,
                }
            ),
            200,
        )
    except InvalidId:
        print("Invalid file_id format. Could not convert to ObjectId.")
        return jsonify({"error": "Invalid file_id format"}), 400

    except FileNotFoundError:
        print("The file could not be found in GridFS.")
        return jsonify({"error": "File not found in GridFS"}), 404

    except PyMongoError as e:
        print("Database operation failed:", str(e))
        return jsonify({"error": "Database operation failed"}), 500


@app.route("/")
def index():
    print("printing documents")
    for document in metadata_collection.find():
        print(document)
    return render_template("index.html")


@app.route("/record")
@login_required
def record():
    """
    Record route
    """
    return render_template("record.html")


@app.route("/upload-audio", methods=["POST"])
@login_required  
def upload_audio():
    """
    Endpoint to upload files and store raw binary in GridFS with metadata.
    Notifies the ML client upon successful storage.
    """
    if "audio" not in request.files or "name" not in request.form:
        return jsonify({"error": "Audio file and name are required"}), 400

    audio_file = request.files["audio"]
    file_name = request.form["name"]
    is_private = request.form.get("private", "false") == "true"  

    gridfs_id = grid_fs.put(
        audio_file,
        filename=file_name,
        content_type=audio_file.mimetype,
    )

    if not gridfs_id:
        return jsonify({"error": "Failed to store the audio file in GridFS"}), 500

    metadata = {
        "file_id": str(gridfs_id),
        "name": file_name,
        "upload_time": datetime.utcnow(),
        "transcription": "",
        "user": current_user.id,
        "is_private": is_private
    }

    metadata_result = metadata_collection.insert_one(metadata)

    if not metadata_result.acknowledged:
        return jsonify({"error": "Failed to store the metadata in the database"}), 500

    print("File successfully uploaded with GridFS ID:", gridfs_id)
    return transcribe(gridfs_id)

@app.route("/user-files")
@login_required
def user_files():
    username = session.get("username")
    user = users_collection.find_one({"username": username})

    if not user:
        print("User not found.", "error")
        return redirect(url_for("login"))

    files = metadata_collection.find({"user": username})
    return render_template("user_files.html", files=files)


@app.route("/public-files")
def public_files():
    files = metadata_collection.find({"is_private": {"$ne": True}})
    return render_template("public_files.html", files=files)

@app.route("/edit-transcription/<file_id>", methods=["GET", "POST"])
@login_required
def edit_transcription(file_id):
    file_metadata = metadata_collection.find_one({"file_id": file_id, "user": current_user.id})

    if not file_metadata:
        print("File not found or you don't have permission to edit it.", "error")
        return redirect(url_for("user_files"))

    if request.method == "POST":
        new_title = request.form["title"]
        new_transcription = request.form["transcription"]
        
        is_private = "private" in request.form  

        result = metadata_collection.update_one(
            {"file_id": file_id, "user": current_user.id},
            {"$set": {
                "name": new_title,
                "transcription": new_transcription,
                "is_private": is_private
            }}
        )

        if result.modified_count > 0:
            print("File updated successfully.", "success")
        else:
            print("No changes were made.", "warning")
        
        return redirect(url_for("user_files"))

    return render_template("edit_transcription.html", file_metadata=file_metadata)


@app.route("/delete-file/<file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    file_metadata = metadata_collection.find_one({"file_id": file_id, "user": current_user.id})
    if not file_metadata:
        print("File not found or you don't have permission to delete it.", "error")
        return redirect(url_for("user_files"))

    for file in grid_fs.find():
            print(f"File ID: {file._id}, Filename: {file.filename}, Content Type: {file.content_type}")
    try:
        file_id_obj = ObjectId(file_id)
    except Exception as e:
        print(f"Invalid file ID: {e}", "error")
        return redirect(url_for("user_files"))   

    try:
        grid_fs.delete(file_id_obj)

        result = metadata_collection.delete_one({"file_id": file_id, "user": current_user.id})

        if result.deleted_count > 0:
            print("File deleted successfully.", "success")
        else:
            print("Failed to delete the metadata.", "error")

    except PyMongoError as e:
        print(f"An error occurred: {e}", "error")
    
    return redirect(url_for("user_files"))

if __name__ == "__main__":
    app.run(port=8080, debug=True)
