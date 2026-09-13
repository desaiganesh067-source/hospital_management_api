# =========================================================
# HELPER FUNCTIONS
# =========================================================

def register_staff(client):
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


def get_staff_token(client):
    response = client.post(
        "/users/login",
        data={
            "username": "staff",
            "password": "staff123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


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


def create_patient_data():
    return {
        "name": "Amit Patil",
        "age": 35,
        "gender": "Male",
        "phone": "9876543210",
        "email": "amit@gmail.com",
        "address": "Chhatrapati Sambhajinagar",
        "date_of_birth": "1991-05-15"
    }


# =========================================================
# CREATE PATIENT TEST
# =========================================================

def test_create_patient(client):
    register_staff(client)

    token = get_staff_token(client)

    response = client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Amit Patil"
    assert data["age"] == 35
    assert data["gender"] == "Male"
    assert data["email"] == "amit@gmail.com"


# =========================================================
# GET ALL PATIENTS TEST
# =========================================================

def test_get_patients(client):
    register_staff(client)

    token = get_staff_token(client)

    client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.get(
        "/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Amit Patil"


# =========================================================
# GET SINGLE PATIENT TEST
# =========================================================

def test_get_single_patient(client):
    register_staff(client)

    token = get_staff_token(client)

    create_response = client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    patient_id = create_response.json()["id"]

    response = client.get(
        f"/patients/{patient_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == patient_id
    assert data["name"] == "Amit Patil"


# =========================================================
# UPDATE PATIENT TEST
# =========================================================

def test_update_patient(client):
    register_staff(client)

    token = get_staff_token(client)

    create_response = client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    patient_id = create_response.json()["id"]

    updated_data = {
        "name": "Amit Updated",
        "age": 36,
        "gender": "Male",
        "phone": "9999999999",
        "email": "amit.updated@gmail.com",
        "address": "Pune",
        "date_of_birth": "1990-05-15"
    }

    response = client.put(
        f"/patients/{patient_id}",
        json=updated_data,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Amit Updated"
    assert data["age"] == 36
    assert data["phone"] == "9999999999"


# =========================================================
# DELETE PATIENT TEST
# =========================================================

def test_delete_patient(client):
    register_admin(client)

    token = get_admin_token(client)

    create_response = client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    patient_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/patients/{patient_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert delete_response.status_code == 204

    # Verify patient is deleted
    get_response = client.get(
        f"/patients/{patient_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert get_response.status_code == 404


# =========================================================
# STAFF CAN CREATE PATIENT
# =========================================================

def test_staff_can_create_patient(client):
    register_staff(client)

    token = get_staff_token(client)

    response = client.post(
        "/patients/",
        json=create_patient_data(),
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201


# =========================================================
# UNAUTHORIZED USER CANNOT ACCESS PATIENTS
# =========================================================

def test_unauthorized_patient_access(client):
    response = client.get("/patients/")

    assert response.status_code == 401