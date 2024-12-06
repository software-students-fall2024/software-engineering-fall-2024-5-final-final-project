def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_login(client):
    response = client.post("/api/login", json={"username": "user", "password": "pw"})
    assert response.status_code == 200
    assert response.json["success"] is True


def test_protected_route(client):
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.get("/api/user-data")
    assert response.status_code == 200
