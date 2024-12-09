import pytest
from app import create_app, mongo
import json
from bson import ObjectId


@pytest.fixture
def client():
    app = create_app("config.TestConfig")

    with app.app_context():
        # Clean test database
        mongo.db.posts.delete_many({})
        mongo.db.users.delete_many({})

    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_token(client):
    """Fixture to get authentication token"""
    # First register a user
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Then login to get token
    response = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    token = json.loads(response.data)["data"]["access_token"]
    return token


@pytest.fixture
def test_post(client, auth_token):
    """Fixture to create a test post"""
    response = client.post(
        "/api/posts",
        json={"title": "Test Post", "content": "Test Content", "tags": ["test"]},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    data = json.loads(response.data)
    return data["data"]["post_id"]


def test_create_post(client, auth_token):
    """Test post creation"""
    response = client.post(
        "/api/posts",
        json={"title": "Test Post", "content": "Test Content", "tags": ["test"]},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "post_id" in data["data"]


def test_get_posts(client):
    """Test getting post list"""
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "data" in data
    assert "total" in data


def test_get_single_post(client, test_post):
    """Test getting a single post"""
    response = client.get(f"/api/posts/{test_post}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "data" in data
    assert data["data"]["title"] == "Test Post"


def test_update_post(client, auth_token, test_post):
    """Test post update"""
    response = client.put(
        f"/api/posts/{test_post}",
        json={
            "title": "Updated Title",
            "content": "Updated Content",
            "tags": ["updated", "test"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Post updated successfully"

    # Verify update
    response = client.get(f"/api/posts/{test_post}")
    data = json.loads(response.data)
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["content"] == "Updated Content"


def test_delete_post(client, auth_token, test_post):
    """Test post deletion"""
    response = client.delete(
        f"/api/posts/{test_post}", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert json.loads(response.data)["message"] == "Post deleted successfully"

    # Verify deletion
    response = client.get(f"/api/posts/{test_post}")
    assert response.status_code == 404


@pytest.fixture
def other_user_token(client):
    """Fixture to get token for another user"""
    # Register another user
    client.post(
        "/api/auth/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123",
        },
    )

    # Login and get token
    response = client.post(
        "/api/auth/login",
        json={"email": "other@example.com", "password": "password123"},
    )
    token = json.loads(response.data)["data"]["access_token"]
    return token


def test_unauthorized_update(client, other_user_token, test_post):
    """Test unauthorized update (trying to update another user's post)"""
    response = client.put(
        f"/api/posts/{test_post}",
        json={"title": "Unauthorized Update", "content": "This update should fail"},
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert response.status_code == 403


def test_unauthorized_delete(client, other_user_token, test_post):
    """Test unauthorized deletion (trying to delete another user's post)"""
    response = client.delete(
        f"/api/posts/{test_post}",
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert response.status_code == 403


def test_get_user_posts(client, auth_token, test_post):
    """Test getting posts for a specific user"""
    # Create another post for the same user
    client.post(
        "/api/posts",
        json={
            "title": "Second Test Post",
            "content": "Second Test Content",
            "tags": ["test"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.get(
        "/api/posts/my-posts", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "data" in data
    assert len(data["data"]) == 2  # Should have two posts


def test_comment_post(client, auth_token, test_post):
    """Test commenting on a post"""
    response = client.post(
        f"/api/posts/{test_post}",
        json={"content": "Test Comment"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data


def test_create_post_invalid_data(client, auth_token):
    response = client.post(
        "/api/posts",
        json={
            "title": "",
            "content": "",
            "tags": []
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


def test_get_posts_pagination(client, auth_token):
    for i in range(15):
        client.post(
            "/api/posts",
            json={
                "title": f"Test Post {i}",
                "content": f"Content {i}",
                "tags": ["test"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    response = client.get("/api/posts?page=1&per_page=10")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 10
    assert data['total'] > 10
    assert 'page' in data

    response = client.get("/api/posts?page=2&per_page=10")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 5


def test_get_posts_with_invalid_pagination(client):
    response = client.get("/api/posts?page=1&per_page=0")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


def test_update_post_invalid_data(client, auth_token, test_post):
    response = client.put(
        f"/api/posts/{test_post}",
        json={
            "title": "",
            "content": "",
            "tags": []
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


def test_invalid_post_id_format(client, auth_token):
    response = client.get("/api/posts/invalid_id")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


def test_comment_invalid_data(client, auth_token, test_post):
    response = client.post(
        f"/api/posts/{test_post}",
        json={"content": ""},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'message' in data


def test_get_post_with_author(client, auth_token, test_post):
    """Test getting a post with author information"""
    response = client.get(f"/api/posts/{test_post}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert 'author_username' in data['data']


def test_post_with_tags(client, auth_token):
    """Test creating a post with tags"""
    response = client.post(
        "/api/posts",
        json={
            "title": "Test Post with Tags",
            "content": "Content with tags",
            "tags": ["test", "tags"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data

def test_update_post_tags(client, auth_token, test_post):
    """Test updating post tags"""
    response = client.put(
        f"/api/posts/{test_post}",
        json={
            "title": "Updated Title",
            "content": "Updated Content",
            "tags": ["updated", "tags"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data

def test_get_post_with_comments(client, auth_token, test_post):
    """Test getting a post with its comments"""
    client.post(
        f"/api/posts/{test_post}",
        json={"content": "Test Comment"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    response = client.get(f"/api/posts/{test_post}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
    assert 'comments' in data['data']
    assert len(data['data']['comments']) > 0

def test_post_author_consistency(client, auth_token):
    """Test post author consistency after creation"""
    response = client.post(
        "/api/posts",
        json={
            "title": "Author Test",
            "content": "Testing author",
            "tags": ["test"]
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    post_id = json.loads(response.data)['data']['post_id']
    
    get_response = client.get(f"/api/posts/{post_id}")
    post_data = json.loads(get_response.data)['data']
    assert 'author_username' in post_data
    assert post_data['author_username'] != "Anonymous"