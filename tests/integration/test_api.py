import os
import pytest
import requests

API_URL = os.getenv('API_URL')
if not API_URL:
    pytest.skip("API_URL environment variable not set", allow_module_level=True)

def test_health_check():
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_item():
    # Create an item
    test_item = {
        "name": "Integration Test Item",
        "description": "This item was created during integration testing"
    }
    create_response = requests.post(f"{API_URL}/items", json=test_item)
    assert create_response.status_code == 200
    created_item = create_response.json()
    assert created_item["name"] == test_item["name"]
    assert created_item["description"] == test_item["description"]

    # Get all items and verify our item is there
    list_response = requests.get(f"{API_URL}/items")
    assert list_response.status_code == 200
    items = list_response.json()
    assert any(item["name"] == test_item["name"] for item in items)
