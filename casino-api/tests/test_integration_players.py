import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.parametrize("name, balance", [
    ("John Doe", 1000),
    ("Jane Doe", 2000),
    ("Alice", 3000),
])
def test_create_multiple_players(test_db, name, balance):
    response = client.post("/players", json={"name": name, "balance": balance})
    assert response.status_code == 201
    player_id = response.json()["id"]

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["name"] == name
    assert response.json()["balance"] == balance


def test_integration_player_lifecycle(test_db):
    response = client.post("/players", json={"name": "John Doe", "balance": 1000})
    assert response.status_code == 201
    player_data = response.json()
    assert "id" in player_data
    player_id = player_data["id"]

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    player_data = response.json()
    assert player_data["name"] == "John Doe"
    assert player_data["balance"] == 1000

    response = client.delete(f"/players/{player_id}")
    assert response.status_code == 200
    deleted_player_data = response.json()
    assert deleted_player_data["name"] == "John Doe"
    assert deleted_player_data["balance"] == 1000

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player with id 1 not found."


def test_update_player(test_db):
    response = client.post("/players", json={"name": "John Doe", "balance": 1000})
    assert response.status_code == 201
    player_id = response.json()["id"]

    response = client.put(f"/players/{player_id}", json={"name": "John Updated", "balance": 1500})
    assert response.status_code == 200
    assert response.json()["name"] == "John Updated"
    assert response.json()["balance"] == 1500

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John Updated"
    assert response.json()["balance"] == 1500


def test_create_player_invalid_data(test_db):
    response = client.post("/players", json={"name": "", "balance": -100})
    assert response.status_code == 422
    assert response.json()["detail"] == "The balance value of -100.0 is not valid. Only positive numbers or zero."


def test_get_non_existent_player(test_db):
    response = client.get("/players/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player with id 9999 not found."


def test_delete_non_existent_player(test_db):
    response = client.delete("/players/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Player with id 9999 not found."


def test_get_all_players(test_db):
    response = client.post("/players", json={"name": "John Doe", "balance": 1000})
    assert response.status_code == 201

    response = client.post("/players", json={"name": "Jane Doe", "balance": 2000})
    assert response.status_code == 201

    response = client.get("/players")
    assert response.status_code == 200
    data = response.json()
    assert len(data["players"]) == 2
    assert data["players"][0]["name"] == "John Doe"
    assert data["players"][1]["name"] == "Jane Doe"
