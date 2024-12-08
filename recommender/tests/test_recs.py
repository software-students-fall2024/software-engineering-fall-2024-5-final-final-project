import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
import json
from recommender.recommender import load_bars, preprocess_bars, combine_features, compute_sim_matrix, recommend_bars

# Mock data for testing

mock_bars_json = {
    "Bar A": ["Pub", "Casual", "Downtown", "Yes", "$$", 4.5],
    "Bar B": ["Lounge", "Romantic", "Uptown", "No", "$$$", 4.0],
    "Bar C": ["Club", "Party", "Midtown", "Yes", "$$$$", 3.5],
    "Bar D": ["Pub", "Casual", "Downtown", "No", "$", 4.0],
    "Bar E": ["Cafe", "Relaxing", "Suburb", "Yes", "$", 5.0],
}

@pytest.fixture
def mock_bars_file():
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_bars_json))):
        yield

@pytest.fixture
def mock_bars_df():
    return pd.DataFrame([
        {"Name": "Bar A", "Type": "Pub", "Occasion": "Casual", "Area": "Downtown", "Reservation": "Yes", "Cost": "$$", "Rating": 4.5},
        {"Name": "Bar B", "Type": "Lounge", "Occasion": "Romantic", "Area": "Uptown", "Reservation": "No", "Cost": "$$$", "Rating": 4.0},
        {"Name": "Bar C", "Type": "Club", "Occasion": "Party", "Area": "Midtown", "Reservation": "Yes", "Cost": "$$$$", "Rating": 3.5},
        {"Name": "Bar D", "Type": "Pub", "Occasion": "Casual", "Area": "Downtown", "Reservation": "No", "Cost": "$", "Rating": 4.0},
        {"Name": "Bar E", "Type": "Cafe", "Occasion": "Relaxing", "Area": "Suburb", "Reservation": "Yes", "Cost": "$", "Rating": 5.0},
    ])

def test_load_bars(mock_bars_file):
    bars_df = load_bars()
    assert len(bars_df) == 5
    assert "Name" in bars_df.columns
    assert bars_df.iloc[0]["Name"] == "Bar A"

def test_preprocess_bars(mock_bars_df):
    processed_df = preprocess_bars(mock_bars_df)
    assert "Combined" in processed_df.columns
    assert processed_df.iloc[0]["Combined"] == "Pub Casual Downtown"

def test_compute_sim_matrix(mock_bars_df):
    processed_df = preprocess_bars(mock_bars_df)
    sim_matrix = compute_sim_matrix(processed_df)
    assert sim_matrix.shape == (len(mock_bars_df), len(mock_bars_df))
    assert np.allclose(np.diag(sim_matrix), 1.0)  # Diagonal should be all ones

def test_recommend_bars(mock_bars_df):
    processed_df = preprocess_bars(mock_bars_df)
    sim_matrix = compute_sim_matrix(processed_df)
    user_bars = ["Bar A"]
    recommendations = recommend_bars(user_bars, processed_df, sim_matrix)

    assert len(recommendations) > 0
    assert recommendations[0]["name"] != "Bar A"  # Bar A shouldn't appear in recommendations
    assert all(key in recommendations[0] for key in ["name", "type", "occasion", "area", "reservation", "cost"])

def test_recommend_bars_no_user_bars(mock_bars_df):
    processed_df = preprocess_bars(mock_bars_df)
    sim_matrix = compute_sim_matrix(processed_df)
    user_bars = []
    recommendations = recommend_bars(user_bars, processed_df, sim_matrix)

    assert recommendations == []

def test_recommend_bars_no_matches(mock_bars_df):
    processed_df = preprocess_bars(mock_bars_df)
    sim_matrix = compute_sim_matrix(processed_df)
    user_bars = ["Nonexistent Bar"]
    recommendations = recommend_bars(user_bars, processed_df, sim_matrix)

    assert recommendations == []

def test_combine_features(mock_bars_df):
    row = mock_bars_df.iloc[0]
    combined = combine_features(row)
    assert combined == "Pub Casual Downtown $$"

@pytest.mark.parametrize("user_bars, expected_length", [
    (["Bar A"], 4),
    (["Bar A", "Bar B"], 3),
    ([], 0),
])
def test_recommend_bars_varied_user_bars(mock_bars_df, user_bars, expected_length):
    processed_df = preprocess_bars(mock_bars_df)
    sim_matrix = compute_sim_matrix(processed_df)
    recommendations = recommend_bars(user_bars, processed_df, sim_matrix)

    assert len(recommendations) == expected_length
