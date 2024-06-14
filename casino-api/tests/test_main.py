# casino-backend/casino-api/tests/test_main.py

from fastapi.testclient import TestClient
from app.main import app  # Importing the FastAPI app instance

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "q": None}

def test_read_item_with_query_param():
    response = client.get("/items/2?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 2, "q": "test"}
