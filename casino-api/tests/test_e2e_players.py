import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.models.player_model import Player
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
    client.post("/players/", json={"name": "Maria da Silva", "balance": 1000})
    client.post("/players/", json={"name": "Pedro da Silva", "balance": 2000})
    
    response = client.get("/players/")
    assert response.status_code == 200
    data = response.json()
    assert "players" in data
    assert len(data["players"]) == 2
    assert data["players"][0]["name"] == "Maria da Silva"
    assert data["players"][1]["name"] == "Pedro da Silva"

def test_read_player(test_db):
    client.post("/players/", json={"name": "Maria da Silva", "balance": 1000})
    response = client.get("/players/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1000
    assert data["id"] == 1

def test_delete_player(test_db):
    client.post("/players/", json={"name": "Maria da Silva", "balance": 1000})
    response = client.delete("/players/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Maria da Silva"
    assert data["balance"] == 1000
    assert data["id"] == 1

    response = client.get("/players/1")
    assert response.status_code == 404
