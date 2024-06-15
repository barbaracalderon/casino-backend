import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.main import app
from app.models.player_model import Player
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

