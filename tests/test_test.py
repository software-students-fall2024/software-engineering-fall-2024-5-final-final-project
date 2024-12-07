import pytest
from io import BytesIO
from app import app
from unittest.mock import patch


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    app.secret_key = "test_secret_key"
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_put():
    with patch("gridfs.GridFS.put") as mock:
        mock.side_effect = Exception("GridFS failure")
        yield mock


def test_upload_audio_gridfs_fail(test_client, mock_put):
    with patch("flask_login.login_required", lambda x: x):
        file_data = (BytesIO(b"audio"), "audio.wav")
        response = test_client.post(
            "/upload-audio",
            data={"audio": file_data, "name": "audio"},
        )
        assert response.status_code == 302


def test_register(test_client):
    response = test_client.get("/register")
    assert response.status_code == 200

    response = test_client.post("/register", data={"username": "", "password": "test123"})
    assert response.status_code == 302

    response = test_client.post("/register", data={"username": "testuser", "password": ""})
    assert response.status_code == 302

    response = test_client.post("/register", data={"username": "newuser", "password": "test123"})
    assert response.status_code == 302


def test_login(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data

    response = test_client.post("/login", data={"username": "", "password": ""})
    assert response.status_code == 302

    response = test_client.post("/login", data={"username": "invaliduser", "password": "wrongpassword"})
    assert response.status_code == 302

    response = test_client.post("/login", data={"username": "newuser", "password": "test123"})

    assert response.status_code == 302


def test_upload_audio_success(test_client, mock_put):
    with patch("flask_login.login_required", lambda x: x):
        file_data = (BytesIO(b"audio"), "audio.wav")
        response = test_client.post(
            "/upload-audio",
            data={"audio": file_data, "name": "audio"},
        )
        assert response.status_code == 302


def test_upload_audio_missing_data(test_client):
    response = test_client.post("/upload-audio", data={"name": "audio"})
    assert response.status_code == 302

    response = test_client.post("/upload-audio", data={"audio": (BytesIO(b"audio"), "audio.wav")})
    assert response.status_code == 302


def test_delete_file(test_client):
    with patch("flask_login.login_required", lambda x: x):
        response = test_client.post("/delete-file/1")
        assert response.status_code == 302


def test_public_files(test_client):
    response = test_client.get("/public-files")
    assert response.status_code == 200
    assert b"Public Files" in response.data
