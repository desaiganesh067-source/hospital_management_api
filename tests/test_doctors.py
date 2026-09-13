# =========================================================
# HELPER FUNCTIONS
# =========================================================

def register_admin(client):
    response = client.post(
        "/users/register",
        json={
            "username": "admin",
            "email": "admin@gmail.com",
            "password": "admin123",
            "role": "admin"
        }
    )

    assert response.status_code == 201

    return response


def get_admin_token(client):
    response = client.post(
        "/users/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_doctor_data():
    return {
        "name": "Dr. Rahul Sharma",
        "specialization": "Cardiology",
        "phone": "9876543210",
        "email": "rahul@gmail.com",
        "available_days": "Monday, Wednesday, Friday"
    }


# =========================================================
# CREATE DOCTOR TEST
# =========================================================

def test_create_doctor(client):
    register_admin(client)

    token = get_admin_token(client)

    response = client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Dr. Rahul Sharma"
    assert data["specialization"] == "Cardiology"
    assert data["email"] == "rahul@gmail.com"


# =========================================================
# GET ALL DOCTORS TEST
# =========================================================

def test_get_doctors(client):
    register_admin(client)

    token = get_admin_token(client)

    client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.get(
        "/doctors/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Dr. Rahul Sharma"


# =========================================================
# GET SINGLE DOCTOR TEST
# =========================================================

def test_get_single_doctor(client):
    register_admin(client)

    token = get_admin_token(client)

    create_response = client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    doctor_id = create_response.json()["id"]

    response = client.get(
        f"/doctors/{doctor_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == doctor_id
    assert data["name"] == "Dr. Rahul Sharma"


# =========================================================
# UPDATE DOCTOR TEST
# =========================================================

def test_update_doctor(client):
    register_admin(client)

    token = get_admin_token(client)

    create_response = client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    doctor_id = create_response.json()["id"]

    updated_data = {
        "name": "Dr. Rahul Updated",
        "specialization": "Neurology",
        "phone": "9999999999",
        "email": "rahul.updated@gmail.com",
        "available_days": "Tuesday, Thursday"
    }

    response = client.put(
        f"/doctors/{doctor_id}",
        json=updated_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Dr. Rahul Updated"
    assert data["specialization"] == "Neurology"
    assert data["phone"] == "9999999999"


# =========================================================
# DELETE DOCTOR TEST
# =========================================================

def test_delete_doctor(client):
    register_admin(client)

    token = get_admin_token(client)

    create_response = client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    doctor_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/doctors/{doctor_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 204

    # Verify doctor no longer exists
    get_response = client.get(
        f"/doctors/{doctor_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code == 404


# =========================================================
# NON-ADMIN CANNOT CREATE DOCTOR
# =========================================================

def test_staff_cannot_create_doctor(client):
    # Register staff user
    response = client.post(
        "/users/register",
        json={
            "username": "staff",
            "email": "staff@gmail.com",
            "password": "staff123",
            "role": "staff"
        }
    )

    assert response.status_code == 201

    # Login staff
    login_response = client.post(
        "/users/login",
        data={
            "username": "staff",
            "password": "staff123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Try creating doctor
    response = client.post(
        "/doctors/",
        json=create_doctor_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"