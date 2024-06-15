import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db_session
from app.main import app
from app.models.player_model import Player

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

def test_integration_player_lifecycle(test_db):
    response = client.post("/players/", json={"name": "John Doe", "balance": 1000})
    assert response.status_code == 201
    player_id = response.json()["id"]

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["balance"] == 1000

    response = client.delete(f"/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["balance"] == 1000

    response = client.get(f"/players/{player_id}")
    assert response.status_code == 404
