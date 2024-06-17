import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.main import app
import logging


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

def create_player(name: str, balance: float) -> int:
    response = client.post("/players", json={"name": name, "balance": balance})
    assert response.status_code == 201
    return response.json()["id"]

def test_create_transaction(test_db):
    player_id = create_player("Alice", 1000.0)
    response = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": "abc123"})
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_id
    assert data["balance"] == 900.0
    assert "id" in data
    assert "txn_uuid" in data

def test_read_transaction(test_db):
    player_id = create_player("Alice", 1000.0)
    response_create = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": "abc123"})
    assert response_create.status_code == 200
    logging.critical(response_create.status_code)
    transaction_uuid = response_create.json()["txn_uuid"]

    response = client.get(f"/transactions/{transaction_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_id
    assert data["value_bet"] == 100.0
    assert data["txn_uuid"] == transaction_uuid

def test_delete_transaction(test_db):
    player_id = create_player("Alice", 1000.0)
    response_create = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": "abc123"})
    assert response_create.status_code == 200
    transaction_id = response_create.json()["id"]

    response_delete = client.delete(f"/transactions/{transaction_id}")
    assert response_delete.status_code == 200

def test_win_transaction(test_db):
    player_id = create_player("Alice", 1000.0)

    response = client.post("/transactions/win", json={"player_id": player_id, "value_win": 500.0, "txn_uuid": "uuid-win-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_id
    assert data["balance"] == 1500.0
    assert data["txn_uuid"] == "uuid-win-1"

    response = client.post("/transactions/win", json={"player_id": player_id, "value_win": 500.0, "txn_uuid": "uuid-win-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_id
    assert data["balance"] == 1500.0
    assert data["txn_uuid"] == "uuid-win-1"

    response = client.post("/transactions/win", json={"player_id": player_id, "value_win": 200.0, "txn_uuid": "uuid-win-2"})
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == player_id
    assert data["balance"] == 1700.0
    assert data["txn_uuid"] == "uuid-win-2"

def test_insufficient_balance(test_db):
    player_id = create_player("Alice", 50.0)
    response = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": "insufficient-balance"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient balance for this operation."

def test_negative_bet_value(test_db):
    player_id = create_player("Alice", 1000.0)
    response = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": -100.0, "txn_uuid": "negative-bet"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Bet value must be positive, not -100.0."

def test_duplicate_transaction_uuid(test_db):
    player_id = create_player("Alice", 1000.0)
    txn_uuid = "duplicate-uuid"
    response1 = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": txn_uuid})
    assert response1.status_code == 200

    response2 = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 200.0, "txn_uuid": txn_uuid})
    assert response2.status_code == 200
    data = response2.json()
    assert data["balance"] == 900.0
    assert data["txn_uuid"] == txn_uuid

def test_negative_win_value(test_db):
    player_id = create_player("Alice", 1000.0)
    response = client.post("/transactions/win", json={"player_id": player_id, "value_win": -500.0, "txn_uuid": "negative-win"})
    assert response.status_code == 422
    assert response.json()["detail"] == "Win value must be positive, not -500.0."

def test_rollback_transaction(test_db):
    player_id = create_player("Alice", 1000.0)
    txn_uuid = "rollback-uuid"
    response_bet = client.post("/transactions/bet", json={"player_id": player_id, "value_bet": 100.0, "txn_uuid": txn_uuid})
    assert response_bet.status_code == 200

    response_rollback = client.post("/transactions/rollback", json={"txn_uuid": txn_uuid, "value_bet": 100.0, "player_id": player_id})
    logging.critical(response_rollback.status_code)
    logging.critical(response_rollback.json())
    assert response_rollback.status_code == 200
    data = response_rollback.json()
    assert data["player_id"] == player_id
    assert data["balance"] == 1000.0
