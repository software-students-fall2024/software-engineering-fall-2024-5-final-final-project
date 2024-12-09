import pytest
from app import app, db, users_collection, bar_data_collection
from pymongo import MongoClient
from bson.objectid import ObjectId

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Now import your app
from app import app, users_collection, bars_collection


# Test configuration
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"

    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def logged_in_user(client):
    # Create a test user
    username = "testuser"
    password = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Insert test user into database
    user = {"username": username, "password": hashed_password}
    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)
# Test configuration
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

# Clean the database before and after each test
@pytest.fixture(autouse=True)
def clean_database():
    users_collection.delete_many({})
    bar_data_collection.delete_many({})
    yield
    users_collection.delete_many({})
    bar_data_collection.delete_many({})

def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_signup(client):
    response = client.post("/signup", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Redirect to login
    assert users_collection.find_one({"username": "testuser"}) is not None

def test_login(client):
    # Create a test user
    hashed_password = bcrypt.hashpw("testpass".encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({"username": "testuser", "password": hashed_password})

    # Login with the correct credentials
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302  # Redirect to dashboard
    assert b"Login successful!" in response.data

def test_dashboard_access(client):
    # Attempt access without logging in
    response = client.get("/dashboard")
    assert response.status_code == 302  # Redirect to login
    assert b"Please log in to access the dashboard." in response.data

def test_savedbar(client):
    # Add a test user and their saved bar
    username = "testuser"
    bar_data_collection.insert_one({"username": username, "name": "Saved Bar"})

    # Log in the user
    with client.session_transaction() as sess:
        sess["username"] = username

    response = client.get("/savedbar")
    assert response.status_code == 200
    assert b"Saved Bar" in response.data

def test_findbar(client):
    # Add a sample bar
    bar_data_collection.insert_one({"name": "Test Bar", "location": "Downtown", "price": "$"})

    # Search by name
    response = client.post("/findbar", data={"filter_type": "name", "search_query": "Test"})
    assert response.status_code == 200
    assert b"Test Bar" in response.data

    # Search by location
    response = client.post("/findbar", data={"filter_type": "location", "location_query": ["Downtown"]})
    assert response.status_code == 200
    assert b"Downtown" in response.data

    # Search by price
    response = client.post("/findbar", data={"filter_type": "price", "price_query": "$"})
    assert response.status_code == 200
    assert b"$" in response.data

def test_delete_transaction(client):
    # Add a test user and a bar
    username = "testuser"
    bar_id = bar_data_collection.insert_one({"username": username, "name": "Delete Me"}).inserted_id

    # Log in the user
    with client.session_transaction() as sess:
        sess["username"] = username

    # Delete the bar
    response = client.post(f"/delete/{bar_id}")
    assert response.status_code == 302  # Redirect after delete
    assert bar_data_collection.find_one({"_id": ObjectId(bar_id)}) is None
