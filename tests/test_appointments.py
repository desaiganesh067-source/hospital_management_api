from datetime import datetime

# -----------------------------
# Helper Functions
# -----------------------------

def register_staff(client):
    response = client.post(
        "/users/register",
        json={
            "username": "staffuser",
            "email": "staff@example.com",
            "password": "password123",
            "role": "staff"
        }
    )
    return response


def get_staff_token(client):
    response = client.post(
        "/users/login",
        data={
            "username": "staffuser",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def register_admin(client):
    response = client.post(
        "/users/register",
        json={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "password123",
            "role": "admin"
        }
    )
    return response


def get_admin_token(client):
    response = client.post(
        "/users/login",
        data={
            "username": "adminuser",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def create_doctor(client, token):
    response = client.post(
        "/doctors/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Dr. John",
            "specialization": "Cardiology",
            "phone": "9876543210",
            "email": "doctor@example.com",
            "available_days": "Monday, Wednesday, Friday"
        }
    )
    return response.json()["id"]


def create_patient(client, token):
    response = client.post(
        "/patients/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Rahul Patil",
            "age": 30,
            "gender": "Male",
            "phone": "9876543211",
            "email": "patient@example.com",
            "address": "Pune",
            "date_of_birth": "1996-01-01"
        }
    )
    return response.json()["id"]


# -----------------------------
# Test 1: Create Appointment
# -----------------------------

def test_create_appointment(client):

    # Admin required because doctor creation is admin-only
    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": "2026-12-01T10:00:00",
            "reason": "Regular checkup"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["reason"] == "Regular checkup"
    assert data["status"] == "scheduled"


# -----------------------------
# Test 2: Get All Appointments
# -----------------------------

def test_get_appointments(client):

    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": "2026-12-01T10:00:00",
            "reason": "Checkup"
        }
    )

    response = client.get(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["doctor_id"] == doctor_id
    assert data[0]["patient_id"] == patient_id


# -----------------------------
# Test 3: Get Single Appointment
# -----------------------------

def test_get_single_appointment(client):

    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    create_response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": "2026-12-02T11:00:00",
            "reason": "Follow up"
        }
    )

    appointment_id = create_response.json()["id"]

    response = client.get(
        f"/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == appointment_id
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id


# -----------------------------
# Test 4: Appointment Conflict
# -----------------------------

def test_appointment_conflict(client):

    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    appointment_data = {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "appointment_time": "2026-12-03T12:00:00",
        "reason": "First appointment"
    }

    first_response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json=appointment_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json=appointment_data
    )

    assert second_response.status_code == 400
    assert "doctor already has an appointment" in second_response.json()["detail"].lower()


# -----------------------------
# Test 5: Update Appointment Status
# -----------------------------

def test_update_appointment_status(client):

    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    create_response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": "2026-12-04T14:00:00",
            "reason": "Consultation"
        }
    )

    appointment_id = create_response.json()["id"]

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "status": "completed"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"


# -----------------------------
# Test 6: Delete Appointment
# -----------------------------

def test_delete_appointment(client):

    register_admin(client)
    token = get_admin_token(client)

    doctor_id = create_doctor(client, token)
    patient_id = create_patient(client, token)

    create_response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_time": "2026-12-05T15:00:00",
            "reason": "Checkup"
        }
    )

    appointment_id = create_response.json()["id"]

    response = client.delete(
        f"/appointments/{appointment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204


# -----------------------------
# Test 7: Invalid Doctor
# -----------------------------

def test_appointment_invalid_doctor(client):

    register_staff(client)
    token = get_staff_token(client)

    patient_id = create_patient(client, token)

    response = client.post(
        "/appointments/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "doctor_id": 9999,
            "patient_id": patient_id,
            "appointment_time": "2026-12-06T16:00:00",
            "reason": "Invalid doctor test"
        }
    )

    assert response.status_code == 404