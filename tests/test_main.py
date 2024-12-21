from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_item():
    test_item = {
        "name": "Test Item",
        "description": "This is a test item"
    }
    response = client.post("/items/", json=test_item)
    assert response.status_code == 200
    assert response.json()["name"] == test_item["name"]
    assert response.json()["description"] == test_item["description"]

def test_get_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
