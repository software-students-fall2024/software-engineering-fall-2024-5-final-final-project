import pytest
from app import create_app, mongo
import json

@pytest.fixture
def client():
    app = create_app('config.TestConfig')
    
    # clean database before testing
    with app.app_context():
        mongo.db.users.delete_many({})
    
    with app.test_client() as client:
        yield client
    
    # clean database after testing
    with app.app_context():
        mongo.db.users.delete_many({})

def test_register(client):
    response = client.post('/api/auth/register', 
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        },
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 201:
        print(f"Response: {response.get_data(as_text=True)}")
        
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'data' in data
    assert data['data']['username'] == 'testuser'
    assert data['data']['email'] == 'test@example.com'

def test_login(client):
    # First register a user
    client.post('/api/auth/register', 
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }
    )

    # Then try to login
    response = client.post('/api/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'password123'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert 'access_token' in data['data']

def test_register_invalid_data(client):
    response = client.post('/api/auth/register', 
        json={
            'username': '',  
            'email': 'invalid_email',  
            'password': '123'  
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data
    error_msg = data['message'].lower()
    assert any(['username' in error_msg, 
               'email' in error_msg,      
               'password' in error_msg])   

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login',
        json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data
    error_msg = data['message'].lower()
    assert any(['invalid' in error_msg,
               'incorrect' in error_msg,
               'not found' in error_msg])

def test_duplicate_registration(client):
    first_response = client.post('/api/auth/register', 
        json={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'password123'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert first_response.status_code == 201
    
    response = client.post('/api/auth/register', 
        json={
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'password123'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'message' in data
    error_msg = data['message'].lower()
    assert any(['exists' in error_msg,
               'already' in error_msg,
               'duplicate' in error_msg])
