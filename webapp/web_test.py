import pytest
from flask import Flask
from pymongo import MongoClient
from pytest_mock_resources import create_mongo_fixture
from bson import ObjectId

mongo = create_mongo_fixture() 

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db(mongo):
    # Access the test MongoDB instance
    client = MongoClient(**mongo.pmr_credentials.as_mongo_kwargs())
    db = client[mongo.config["mockdb"]]
    yield db


def test_home_logged_out(client):
    # If not logged in, home redirects to login
    response = client.get("/main", follow_redirects=True)
    assert b"Login" in response.data or b"Invalid credentials" in response.data

def test_home_logged_in(client, monkeypatch):
    # Mock the globals to simulate a logged-in user
    monkeypatch.setattr("app.logged_in", True)
    monkeypatch.setattr("app.username", "testuser")

    response = client.get("/main")
    assert response.status_code == 200
    # Check that the username is displayed or something unique from 'home.html'
    assert b"testuser" in response.data

def test_groups_no_login(client):
    # No login scenario should redirect to login
    response = client.get("/groups", follow_redirects=True)
    assert b"Login" in response.data

def test_groups_logged_in(client, db, monkeypatch):
    # Insert a user and a group in the test db
    user_id = ObjectId()
    group_id = ObjectId()
    db["USERS"].insert_one({
        "_id": user_id,
        "name": "testuser",
        "password": "testpass",
        "groups": [group_id]
    })
    db["GROUPS"].insert_one({
        "_id": group_id,
        "group_name": "Test Group",
        "group_members": [
            {"user_id": user_id, "name": "testuser"}
        ],
        "expenses": []
    })

    monkeypatch.setattr("app.logged_in", True)
    monkeypatch.setattr("app.username", "testuser")

    response = client.get("/groups")
    assert response.status_code == 200
    assert b"Test Group" in response.data

def test_create_group_logged_out(client):
    # Trying to create a group without login should redirect
    response = client.get("/create-group", follow_redirects=True)
    assert b"Login" in response.data

def test_create_group_logged_in(client, db, monkeypatch):
    # Insert a user who will create the group
    user_id = ObjectId()
    db["USERS"].insert_one({
        "_id": user_id,
        "name": "creator",
        "password": "secret",
        "groups": []
    })

    # Also insert another user to add as a member
    member_id = ObjectId()
    db["USERS"].insert_one({
        "_id": member_id,
        "name": "memberuser",
        "password": "secret2",
        "groups": []
    })

    monkeypatch.setattr("app.logged_in", True)
    monkeypatch.setattr("app.username", "creator")

    # Post a new group creation
    response = client.post("/create-group", data={
        "group_name": "Vacation",
        "members": "memberuser"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Group 'Vacation' created successfully!" in response.data

    # Check the DB to ensure the group was created
    group = db["GROUPS"].find_one({"group_name": "Vacation"})
    assert group is not None
    assert len(group["group_members"]) == 1
    assert group["group_members"][0]["name"] == "memberuser"

    # Check that user groups got updated
    creator_user = db["USERS"].find_one({"name": "creator"})
    member_user = db["USERS"].find_one({"name": "memberuser"})
    assert group["_id"] in creator_user["groups"]
    assert group["_id"] in member_user["groups"]
