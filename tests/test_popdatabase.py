import os
import pytest
from unittest.mock import patch, MagicMock
from pymongo import MongoClient


categories = {
    "cold": {"min": -10, "max": 0},
    "cool": {"min": 1, "max": 15},
    "warm": {"min": 16, "max": 25},
    "hot": {"min": 26, "max": 40},
}
images_folder = "./images"


@pytest.fixture
def mock_db():
    """Mock the MongoDB"""
    with patch("pymongo.MongoClient") as mock_client:
        mock_db=MagicMock()
        mock_client.return_value={"Outfits": mock_db}
        yield mock_db


@pytest.fixture
def mock_os():
    """Mock os module."""
    with patch("os.path.exists") as mock_exists, patch("os.listdir") as mock_listdir:
        yield mock_exists,mock_listdir


def test_outfit_data_insertion(mock_db, mock_os):
    """Test that outfit data is prepared and inserted correctly."""
    mock_exists, mock_listdir=mock_os
    mock_exists.side_effect=lambda path: "cold" in path or "warm" in path
    mock_listdir.side_effect=lambda path: ["image1.jpg", "image2.png"] if "cold" in path else ["image3.jpg"]

    mock_outfits_collection = mock_db.outfits
    mock_outfits_collection.insert_many = MagicMock()
    expected_data=[
        {
            "temperature_range": {"min": -10, "max": 0},
            "weather_condition": "cold",
            "image_url": "/images/cold/image1.jpg",
        },
        {
            "temperature_range": {"min": -10, "max": 0},
            "weather_condition": "cold",
            "image_url": "/images/cold/image2.png",
        },
        {
            "temperature_range": {"min": 16, "max": 25},
            "weather_condition": "warm",
            "image_url": "/images/warm/image3.jpg",
        },
    ]

    outfit_data=[]
    for category,temp_range in categories.items():
        category_folder=os.path.join(images_folder, category)
        if os.path.exists(category_folder):
            images=[img for img in os.listdir(category_folder) if img.endswith((".jpg", ".png"))]
            for image in images:
                outfit_data.append({
                    "temperature_range": temp_range,
                    "weather_condition": category,
                    "image_url": f"/images/{category}/{image}"
                })
        else:
            print(f"Folder for category '{category}' does not exist. Skipping...")

    if outfit_data:
        mock_outfits_collection.insert_many(outfit_data)

    mock_outfits_collection.insert_many.assert_called_once_with(expected_data)


def test_no_images_in_folders(mock_db, mock_os):
    """Test when there arent any pics in folders."""
    mock_exists, mock_listdir=mock_os
    mock_exists.return_value=True
    mock_listdir.side_effect=lambda path:[]

    mock_outfits_collection = mock_db.outfits
    mock_outfits_collection.insert_many=MagicMock()
    outfit_data=[]
    for category, temp_range in categories.items():
        category_folder=os.path.join(images_folder, category)
        if os.path.exists(category_folder):
            images=[img for img in os.listdir(category_folder) if img.endswith((".jpg", ".png"))]
            for image in images:
                outfit_data.append({
                    "temperature_range": temp_range,
                    "weather_condition": category,
                    "image_url": f"/images/{category}/{image}"
                })
        else:
            print(f"Folder for category '{category}' does not exist. Skipping...")
    assert not outfit_data
    mock_outfits_collection.insert_many.assert_not_called()


def test_missing_folders(mock_db, mock_os):
    """Test when the temp folders are missing."""
    mock_exists, mock_listdir=mock_os
    mock_exists.side_effect=lambda path: "cold" in path
    mock_listdir.side_effect=lambda path: ["image1.jpg", "image2.png"] if "cold" in path else []
    mock_outfits_collection=MagicMock()
    mock_db.outfits=mock_outfits_collection
    outfit_data=[]
    for category,temp_range in categories.items():
        category_folder=os.path.join(images_folder, category)
        if os.path.exists(category_folder):
            images=[img for img in os.listdir(category_folder) if img.endswith((".jpg", ".png"))]
            for image in images:
                outfit_data.append({
                    "temperature_range":temp_range,
                    "weather_condition":category,
                    "image_url": f"/images/{category}/{image}"
                })
        else:
            print(f"Folder for category '{category}' does not exist. Skipping...")
    if outfit_data:
        mock_db.outfits.insert_many(outfit_data)
    expected_data=[
        {
            "temperature_range": {"min": -10, "max": 0},
            "weather_condition": "cold",
            "image_url": "/images/cold/image1.jpg",
        },
        {
            "temperature_range": {"min": -10, "max": 0},
            "weather_condition": "cold",
            "image_url": "/images/cold/image2.png",
        },
    ]
    assert outfit_data==expected_data
    mock_db.outfits.insert_many.assert_called_once_with(expected_data)
