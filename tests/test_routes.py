def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_login(client):
    # Ensure the password in the database is hashed before running this test
    response = client.post("/api/login", json={"username": "user", "password": "pw"})
    assert response.status_code == 200
    assert response.json["success"] is True


def test_invalid_login(client):
    response = client.post(
        "/api/login", json={"username": "user", "password": "wrong_pw"}
    )
    assert response.status_code == 401


def test_login_no_username(client):
    response = client.post("/api/login", json={"username": "user"})
    assert response.status_code == 400


def test_login_no_password(client):
    response = client.post("/api/login", json={"password": "pw"})
    assert response.status_code == 400


def test_protected_route(client):
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.get("/api/user-data")
    assert response.status_code == 200


def test_logout(client):
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.post("/api/logout")
    assert response.status_code == 200
    assert response.json["success"] is True
