import os
from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from gridfs import GridFS
import requests
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from pydub import AudioSegment
import speech_recognition as sr

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')  

mongodb_username = os.getenv('MONGODB_USERNAME') 
mongodb_password = os.getenv('MONGODB_PASSWORD')

db_uri = f"mongodb://{mongodb_username}:{mongodb_password}@mongodb:27017"
client = MongoClient(db_uri)
db = client["audio_db"]
grid_fs = GridFS(db)
metadata_collection = db["audio_metadata"]


def fetch_and_convert_to_wav(file_id):
    """
    Fetch binary audio from GridFS and convert it to WAV format.
    """
    grid_file = grid_fs.get(file_id)
    content_type = grid_file.content_type  
    print(content_type)

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
    file_id = request.args.get("file_id")
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/record")
def record():
    """
    Record route
    """
    return render_template("record.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    """
    Endpoint to upload files and store raw binary in GridFS with metadata.
    Notifies the ML client upon successful storage.
    """
    if "audio" not in request.files or "name" not in request.form:
        return jsonify({"error": "Audio file and name are required"}), 400

    audio_file = request.files["audio"]
    file_name = request.form["name"]

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
    }

    metadata_result = metadata_collection.insert_one(metadata)

    if not metadata_result.acknowledged:
        return jsonify({"error": "Failed to store the metadata in the database"}), 500

    print("File successfully uploaded with GridFS ID:", gridfs_id)
    return transcribe(gridfs_id)

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "8080")
    app.run(port=FLASK_PORT)
