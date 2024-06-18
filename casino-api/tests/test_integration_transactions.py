import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.main import app
from app.models.player_model import Player
from app.models.transaction_model import Transaction

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

def create_player(test_db, name: str, balance: float) -> Player:
    player = Player(name=name, balance=balance)
    test_db.add(player)
    test_db.commit()
    test_db.refresh(player)
    return player

def create_transaction(test_db, player_id: int, value_bet: float, txn_uuid: str) -> Transaction:
    transaction = Transaction(player_id=player_id, value_bet=value_bet, txn_uuid=txn_uuid)
    test_db.add(transaction)
    test_db.commit()
    test_db.refresh(transaction)
    return transaction

def test_create_transaction_integration(test_db):
    with TestingSessionLocal() as db:
        player = create_player(db, "Alice", 1000.0)
        response = client.post("/transactions/bet", json={"player_id": player.id, "value_bet": 100.0, "txn_uuid": "abc123"})
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player.id
        assert data["balance"] == 900.0
        assert "id" in data
        assert "txn_uuid" in data

def test_read_transaction_integration(test_db):
    with TestingSessionLocal() as db:
        player = create_player(db, "Alice", 1000.0)
        transaction = create_transaction(db, player.id, 100.0, "abc123")
        response = client.get(f"/transactions/{transaction.txn_uuid}")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player.id
        assert data["value_bet"] == 100.0
        assert data["txn_uuid"] == transaction.txn_uuid

def test_delete_transaction_integration(test_db):
    with TestingSessionLocal() as db:
        player = create_player(db, "Alice", 1000.0)
        transaction = create_transaction(db, player.id, 100.0, "abc123")
        response = client.delete(f"/transactions/{transaction.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction.id

def test_read_transactions_integration(test_db):
    with TestingSessionLocal() as db:
        player = create_player(db, "Alice", 1000.0)
        create_transaction(db, player.id, 100.0, "abc123")
        create_transaction(db, player.id, 200.0, "def456")

        response = client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 2
        assert data["transactions"][0]["value_bet"] == 100.0
        assert data["transactions"][1]["value_bet"] == 200.0


def test_rollback_transaction_not_found(test_db):
    with TestingSessionLocal() as db:
        response = client.post("/transactions/rollback", json={"txn_uuid": "notfound123", "value_bet": 200.0, "player_id": 1})
        assert response.status_code == 404
        assert "Transaction not found, but stored with id:" in response.json()["detail"]
