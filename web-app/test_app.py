"""
Unit tests for the Flask application defined in `app.py`.
"""

# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

# pylint web-app/
# black .


from unittest.mock import patch, MagicMock
from io import BytesIO
from flask.testing import FlaskClient
import pytest
from bson.objectid import ObjectId
import requests
from app import app, generate_stats_doc, retry_request


@pytest.fixture(name="flask_client")
def flask_client_fixture():
    """
    Provide a Flask test client for testing application routes.
    Yields:
        FlaskClient: A test client for the Flask application.
    """
    app.config["TESTING"] = True
    with app.test_client() as temp_client:
        yield temp_client


@patch("app.collection")
def test_generate_stats_doc(mock_collection):
    """
    tests that the `generate_stats_doc` function inserts a document
    into the database and correctly returns its ID.

    Args:
        mock_collection (MagicMock): Mock database collection to simulate
        `insert_one` behavior.

    """
    mock_inserted_id = ObjectId()
    mock_collection.insert_one.return_value.inserted_id = mock_inserted_id

    _id = generate_stats_doc()

    mock_collection.insert_one.assert_called_once()
    assert _id == str(mock_inserted_id)


# Tests for retry_request
@patch("app.requests.post")
def test_retry_request_success_on_first_try(mock_post):
    """
    Verifies that the `retry_request` function can make a POST request
    and return the response without retries if the initial attempt succeeds.

    Args:
        mock_post (MagicMock): Mock `requests.post` method to simulate a successful HTTP request.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files)
    assert response == mock_response
    mock_post.assert_called_once()


@patch("app.requests.post")
def test_retry_request_success_after_retries(mock_post):
    """
    Verifies the `retry_request` function handles HTTP errors

    Args:
        mock_post (MagicMock): Mocked `requests.post` method to simulate HTTP failures
        on initial attempts and a successful response on a retry.
    """

    # Create a mock response object
    mock_response = MagicMock()
    # Simulate exceptions on the first two attempts, then succeed
    mock_response.raise_for_status.side_effect = [
        requests.exceptions.HTTPError("Connection error"),
        requests.exceptions.HTTPError("Timeout"),
        None,  # Success on third attempt
    ]
    # Always return the mock_response from requests.post
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response == mock_response
    assert mock_post.call_count == 3
    assert mock_response.raise_for_status.call_count == 3


@patch("app.requests.post")
def test_retry_request_all_failures(mock_post):
    """
    Tests the `retry_request` function when all retry attempts fail.

    Args:
        mock_post (MagicMock): Mocked `requests.post` method to simulate HTTP failures
        for all retry attempts.
    """
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Connection error"
    )
    mock_post.return_value = mock_response

    url = "http://example.com/predict"
    files = {"image": MagicMock()}

    response = retry_request(url, files, retries=3, delay=0)
    assert response is None
    assert mock_post.call_count == 3
    assert mock_response.raise_for_status.call_count == 3


# Tests for routes
@patch("app.generate_stats_doc", return_value=str(ObjectId()))
def test_home_route(mock_generate_stats_doc, flask_client):
    """
    Test the home route of the application.

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    response = flask_client.get("/")
    _ = mock_generate_stats_doc
    assert response.status_code == 200
    assert "db_object_id" in response.headers["Set-Cookie"]


@patch("app.generate_stats_doc", return_value=str(ObjectId()))
def test_home_route_with_existing_cookie(mock_generate_stats_doc, flask_client):
    """
    Test home route when a db_object_id cookie already exists.

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    _ = mock_generate_stats_doc
    flask_client.set_cookie("db_object_id", str(ObjectId()))
    response = flask_client.get("/")
    assert response.status_code == 200


@patch("app.generate_stats_doc", return_value=str(ObjectId()))
def test_index_route(mock_generate_stats_doc, flask_client: FlaskClient):
    """
    Test index route

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    _ = mock_generate_stats_doc
    response = flask_client.get("/index")
    assert response.status_code == 200


@patch("app.collection")
@patch("app.generate_stats_doc", return_value=str(ObjectId()))
def test_statistics_route(
    mock_generate_stats_doc, mock_collection, flask_client: FlaskClient
):
    """
    Test statistics page route

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    stats = {
        "Rock": {"wins": 1, "losses": 0, "ties": 0, "total": 1},
        "Paper": {"wins": 0, "losses": 1, "ties": 0, "total": 1},
        "Scissors": {"wins": 0, "losses": 0, "ties": 1, "total": 1},
        "Totals": {"wins": 1, "losses": 1, "ties": 1},
    }
    mock_collection.find_one.return_value = stats
    _ = mock_generate_stats_doc

    response = flask_client.get("/statistics")
    assert response.status_code == 200
    assert b"Statistics" in response.data


@patch("app.retry_request")
@patch("app.collection.update_one")
def test_result_route_success(
    mock_retry_request, mock_update_one, flask_client: FlaskClient
):
    """
    Test results route for a successful request

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Scissors"}
    mock_retry_request.return_value = mock_response

    mock_id = ObjectId()
    flask_client.set_cookie("db_object_id", str(mock_id))

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post(
        "/result", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"AI wins!" in response.data
    _ = mock_update_one


@patch("app.retry_request")
def test_result_route_unknown_gesture(mock_retry_request, flask_client: FlaskClient):
    """
    Test result route for when the user's gesture is unable to be recognised

    Args:
        client (FlaskClient): Flask client used to simulate HTTP requests.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"gesture": "Unknown"}
    mock_retry_request.return_value = mock_response

    mock_id = ObjectId()
    flask_client.set_cookie("db_object_id", str(mock_id))

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post(
        "/result", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"Gesture not recognized" in response.data


@patch("app.retry_request")
def test_result_route_ml_failure(mock_retry_request, flask_client: FlaskClient):
    """
    Test the result route when the model fails to predict

    Args:
        mock_retry_request (MagicMock): Mocked retry_request function to simulate failure.
        client (FlaskClient):  Flask client used to simulate HTTP requests.
    """
    mock_retry_request.return_value = None

    mock_id = ObjectId()
    flask_client.set_cookie("db_object_id", str(mock_id))

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post(
        "/result", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert b"No valid prediction" in response.data


@patch("app.retry_request")
def test_result_route_no_image(mock_retry_request, flask_client: FlaskClient):
    """
    Test the result route when there is no image

    Args:
        client (FlaskClient):  Flask client used to simulate HTTP requests.
    """
    response = flask_client.post("/result", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"No image file provided" in response.data
    mock_retry_request.assert_not_called()





