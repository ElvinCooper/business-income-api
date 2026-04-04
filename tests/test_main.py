from fastapi.testclient import TestClient


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Business Income API"
    assert "version" in data


def test_404_for_nonexistent_route(client):
    response = client.get("/nonexistent-route")
    assert response.status_code == 404


def test_405_for_wrong_method(client):
    response = client.delete("/")
    assert response.status_code == 405


def test_exception_handlers_registered(client):
    assert hasattr(client.app, "exception_handlers")
    handlers = client.app.exception_handlers
    assert Exception in handlers
