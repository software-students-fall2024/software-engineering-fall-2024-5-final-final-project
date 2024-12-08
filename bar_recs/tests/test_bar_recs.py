import pytest
from flask.testing import FlaskClient
from unittest.mock import patch, MagicMock
from bson import ObjectId
from surprise import Dataset, Reader
import pandas as pd
from bar_recs.bar_recs import (
    app,
    add_bar,
    get_all_bars,
    add_rating,
    recommend_bars_for_user,
    load_ratings_data,
    train_recommender_system,
    db,
)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_bar_route(client: FlaskClient):
    bar_data = {"name": "Test Bar", "location": "Test Location"}
    with patch("bar_recs.bar_recs.add_bar") as mock_add_bar:
        mock_add_bar.return_value = MagicMock(inserted_id=ObjectId("123456789012345678901234"))
        response = client.post("/add_bar", json=bar_data)
        assert response.status_code == 201
        assert "bar_id" in response.json
        mock_add_bar.assert_called_once_with(bar_data)


def test_add_rating_route(client: FlaskClient):
    rating_data = {"user_id": "1", "bar_id": "101", "rating": 4.5}
    with patch("bar_recs.bar_recs.add_rating") as mock_add_rating:
        mock_add_rating.return_value = MagicMock(inserted_id=ObjectId("123456789012345678901234"))
        response = client.post("/add_rating", json=rating_data)
        assert response.status_code == 201
        assert "rating_id" in response.json
        mock_add_rating.assert_called_once_with(rating_data)


def test_get_bars_route(client: FlaskClient):
    mock_bars = [{"_id": "1", "name": "Bar 1"}, {"_id": "2", "name": "Bar 2"}]
    with patch("bar_recs.bar_recs.get_all_bars", return_value=mock_bars):
        response = client.get("/get_bars")
        assert response.status_code == 200
        assert response.get_json() == mock_bars


def test_recommend_route(client: FlaskClient):
    user_id = "1"
    mock_recommendations = [{"_id": "1", "name": "Recommended Bar 1"}]
    with patch("bar_recs.bar_recs.recommend_bars_for_user", return_value=mock_recommendations):
        response = client.get(f"/recommend/{user_id}")
        assert response.status_code == 200
        assert response.get_json() == mock_recommendations



def test_recommend_bars_for_user():
    user_id = "1"
    mock_bars = [{"_id": "1", "name": "Bar 1"}, {"_id": "2", "name": "Bar 2"}]
    mock_ratings = [{"user_id": "1", "bar_id": "3", "rating": 4.5}]
    with patch("bar_recs.bar_recs.get_all_bars", return_value=mock_bars), \
         patch("bar_recs.bar_recs.db.ratings.find", return_value=mock_ratings), \
         patch("bar_recs.bar_recs.recommender_algo") as mock_algo:
        mock_algo.predict.return_value = MagicMock(est=4.0)
        result = recommend_bars_for_user(user_id)
        assert len(result) == 2
        assert result[0]["name"] in ["Bar 1", "Bar 2"]

def test_train_recommender_system():
    mock_dataset = MagicMock(spec=Dataset)
    with patch("bar_recs.bar_recs.load_ratings_data", return_value=mock_dataset), \
         patch("bar_recs.bar_recs.train_test_split", return_value=(MagicMock(), MagicMock())), \
         patch("bar_recs.bar_recs.SVD") as mock_svd:
        mock_svd.return_value = MagicMock()
        algo, trainset = train_recommender_system()
        assert algo is not None
        assert trainset is not None

def test_load_ratings_data():
    mock_ratings = [
        {"user_id": "1", "bar_id": "101", "rating": 4.5},
        {"user_id": "2", "bar_id": "102", "rating": 3.0},
        {"user_id": "3", "bar_id": "103", "rating": 5.0},
    ]

    with patch("bar_recs.bar_recs.db.ratings.find", return_value=mock_ratings):
        dataset = load_ratings_data()

        assert dataset is not None
        assert isinstance(dataset, Dataset)
