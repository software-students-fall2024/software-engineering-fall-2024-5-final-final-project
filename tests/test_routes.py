"""
This file tests the routes necessary for 80% coverage
"""


def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200


def test_login(client):
    """Ensure the password in the database is hashed before running this test"""
    response = client.post("/api/login", json={"username": "user", "password": "pw"})
    assert response.status_code == 200
    assert response.json["success"] is True


def test_invalid_login(client):
    """Test login with an invalid."""
    response = client.post(
        "/api/login", json={"username": "user", "password": "wrong_pw"}
    )
    assert response.status_code == 401


def test_login_no_username(client):
    """Test login with no username."""
    response = client.post("/api/login", json={"username": "user"})
    assert response.status_code == 400


def test_login_no_password(client):
    """Test login with no password."""
    response = client.post("/api/login", json={"password": "pw"})
    assert response.status_code == 400


def test_protected_route(client):
    """Test protected routes for authentication."""
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.get("/api/user-data")
    assert response.status_code == 200


def test_logout(client):
    """Test logout and response."""
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.post("/api/logout")
    assert response.status_code == 200
    assert response.json["success"] is True


def test_update_budget(client):
    """Test updating the budget."""
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.post("/api/update-budget", json={"budget": 500.00})
    assert response.status_code == 200
    assert response.json["success"] is True


def test_add_expense(client):
    """Test adding an expense."""
    client.post("/api/login", json={"username": "user", "password": "pw"})
    response = client.post(
        "/api/add-expense", json={"amount": 50.00, "description": "Groceries"}
    )
    assert response.status_code == 200
    assert response.json["success"] is True


# def test_remove_expense(client):
#     """Test removing an expense."""
#     client.post("/api/login", json={"username": "user", "password": "pw"})
#     client.post("/api/add-expense", json={"amount": 50.00, "description": "Groceries"})
#     expenses_response = client.get("/api/expenses")
#     expense_id = expenses_response.json[0]["id"]
#     response = client.post("/api/remove-expense", json={"expense_id": expense_id})
#     assert response.status_code == 200
#     assert response.json["success"] is True


# def test_get_expenses(client):
#     """Test getting the expenses."""
#     client.post("/api/login", json={"username": "user", "password": "pw"})
#     client.post("/api/add-expense", json={"amount": 50.00, "description": "Groceries"})
#     client.post("/api/add-expense", json={"amount": 20.00, "description": "Transport"})
#     response = client.get("/api/expenses")
#     assert response.status_code == 200
#     assert len(response.json) == 2
#     assert (
#         response.json[0]["description"] == "Transport"
#     )  # Sorted by date, latest first


def test_predict_expenses(client):
    """
    Test the predict_expenses route and clean up test data after execution.
    """
    # Log in first to access protected routes
    response = client.post("/api/login", json={"username": "user", "password": "pw"})
    assert response.status_code == 200
    assert response.json["success"] is True

    # Add the sample expenses
    response1 = client.post(
        "/api/add-expense",
        json={"amount": 100.0, "description": "Groceries"},
    )
    response2 = client.post(
        "/api/add-expense",
        json={"amount": 200.0, "description": "Utilities"},
    )
    response3 = client.post(
        "/api/add-expense",
        json={"amount": 300.0, "description": "Rent"},
    )
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    # Fetch expenses to verify they were added
    response = client.get("/api/expenses")
    expenses = response.json
    assert len(expenses) > 0  # Ensure expenses exist for the prediction test

    # Call the predict_expenses route
    response = client.get("/api/predict-expenses")
    assert response.status_code == 200
    assert "predicted_expenses" in response.json
    assert isinstance(response.json["predicted_expenses"], float)

    # Clean up: Remove the expenses added during the test
    for expense in expenses:
        client.post(
            "/api/remove-expense",
            json={"expense_id": expense["id"]},
        )


def test_predict_expenses_no_data(client):
    """
    Test the predict_expenses route when no data is available.
    """
    # Log in first to access protected routes
    response = client.post("/api/login", json={"username": "user", "password": "pw"})
    assert response.status_code == 200
    assert response.json["success"] is True

    # Call the predict_expenses endpoint without adding expenses
    response = client.get("/api/predict-expenses")
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "No valid expense data available for prediction"
