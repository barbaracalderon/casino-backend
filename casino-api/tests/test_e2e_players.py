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

def test_create_player(test_db):
    response = client.post("/players/", json={"name": "Maria da Silva", "balance": 1000})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1000
    assert "id" in data

def test_read_players(test_db):
    client.post("/players", json={"name": "Maria da Silva", "balance": 1000})
    client.post("/players", json={"name": "Pedro da Silva", "balance": 2000})
    
    response = client.get("/players")
    assert response.status_code == 200
    data = response.json()
    assert "players" in data
    assert len(data["players"]) == 2
    assert data["players"][0]["name"] == "Maria da Silva"
    assert data["players"][1]["name"] == "Pedro da Silva"

def test_read_player(test_db):
    client.post("/players", json={"name": "Maria da Silva", "balance": 1000})
    response = client.get("/players/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1000
    assert data["id"] == 1

def test_delete_player(test_db):
    client.post("/players", json={"name": "Maria da Silva", "balance": 1000})
    response = client.delete("/players/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1000
    assert data["id"] == 1

    response = client.get("/players/1")
    assert response.status_code == 404

def test_create_player_invalid_data(test_db):
    response = client.post("/players", json={"name": "", "balance": -100})
    assert response.status_code == 422

def test_read_nonexistent_player(test_db):
    response = client.get("/players/999")
    assert response.status_code == 404

def test_delete_nonexistent_player(test_db):
    response = client.delete("/players/999")
    assert response.status_code == 404

def test_update_player(test_db):
    client.post("/players", json={"name": "Maria da Silva", "balance": 1000})
    response = client.put("/players/1", json={"name": "Maria da Silva", "balance": 1500})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1500

def test_get_player_transaction_history(test_db):
    client.post("/players", json={"name": "Maria da Silva", "balance": 1000})
    client.post("/transactions/bet", json={"player_id": 1, "value_bet": 5, "txn_uuid": "abcd"})
    client.post("/transactions/win", json={"player_id": 1, "value_win": 1000, "txn_uuid": "efgh"})
    client.post("/transactions/rollback", json={"player_id": 1, "value_bet": 20, "txn_uuid": "ijkl"})

    response = client.get("/players/1/history")

    assert response.status_code == 200
    data = response.json()
    assert data["player"] == 1
    assert len(data["history"]) == 3

    assert data["history"][0]["txn_uuid"] == "abcd"
    assert data["history"][0]["type"] == "bet"
    assert data["history"][0]["value"] == 5
    assert data["history"][0]["rolled_back"] is False

    assert data["history"][1]["txn_uuid"] == "efgh"
    assert data["history"][1]["type"] == "win"
    assert data["history"][1]["value"] == 1000
    assert data["history"][1]["rolled_back"] is False

    assert data["history"][2]["txn_uuid"] == "ijkl"
    assert data["history"][2]["type"] == "bet"
    assert data["history"][2]["value"] == 20
    assert data["history"][2]["rolled_back"] is True


def test_get_player_transaction_history_player_not_found(test_db):
    response = client.get("/players/999/history")

    assert response.status_code == 404
    assert response.json() == {"detail": "Player with id 999 not found."}