def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Hospital Management API is running"


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"