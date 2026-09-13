# =========================================================
# REGISTER USER TEST
# =========================================================

def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@gmail.com"
    assert data["role"] == "staff"

    # Password should NOT be returned
    assert "password" not in data


# =========================================================
# DUPLICATE USERNAME TEST
# =========================================================

def test_duplicate_username(client):
    user_data = {
        "username": "duplicateuser",
        "email": "duplicate1@gmail.com",
        "password": "test123456",
        "role": "staff"
    }

    # First registration
    first_response = client.post(
        "/users/register",
        json=user_data
    )

    assert first_response.status_code == 201

    # Second registration with same username
    second_response = client.post(
        "/users/register",
        json={
            "username": "duplicateuser",
            "email": "duplicate2@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Username already exists"
    )


# =========================================================
# DUPLICATE EMAIL TEST
# =========================================================

def test_duplicate_email(client):
    first_response = client.post(
        "/users/register",
        json={
            "username": "userone",
            "email": "same@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/users/register",
        json={
            "username": "usertwo",
            "email": "same@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    assert second_response.status_code == 400
    assert second_response.json()["detail"] == (
        "Email already exists"
    )


# =========================================================
# LOGIN TEST
# =========================================================

def test_login_user(client):
    # Register user
    client.post(
        "/users/register",
        json={
            "username": "loginuser",
            "email": "loginuser@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    # Login
    response = client.post(
        "/users/login",
        data={
            "username": "loginuser",
            "password": "test123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# =========================================================
# WRONG PASSWORD TEST
# =========================================================

def test_wrong_password(client):
    # Register user
    client.post(
        "/users/register",
        json={
            "username": "wrongpassuser",
            "email": "wrongpass@gmail.com",
            "password": "test123456",
            "role": "staff"
        }
    )

    # Login with wrong password
    response = client.post(
        "/users/login",
        data={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid username or password"
    )