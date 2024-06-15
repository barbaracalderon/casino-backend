import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services.player_service import PlayerService
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from app.schemas.player_schema import PlayerResponse, PlayerCreate
from typing import List

@pytest.fixture
def mock_player_repository():
    return MagicMock()

@pytest.fixture
def player_service(mock_player_repository):
    return PlayerService(mock_player_repository)

def test_create_player(player_service, mock_player_repository):
    player_create_data = PlayerCreate(name="Maria da Silva", balance=1000)
    mock_db_session = MagicMock(spec=Session)

    mock_player_repository.create_player.return_value = PlayerResponse(id=1, name="Maria da Silva", balance=1000)

    created_player = player_service.create_player(db=mock_db_session, player=player_create_data)

    assert created_player.id == 1
    assert created_player.name == "Maria da Silva"
    assert created_player.balance == 1000

def test_get_player(player_service, mock_player_repository):
    mock_player_repository.get_player.return_value = PlayerResponse(id=1, name="Maria da Silva", balance=1000)

    found_player = player_service.get_player(db=MagicMock(), player_id=1)

    assert found_player.id == 1
    assert found_player.name == "Maria da Silva"
    assert found_player.balance == 1000

def test_delete_player(player_service, mock_player_repository):
    mock_player_repository.delete_player.return_value = PlayerResponse(id=1, name="Maria da Silva", balance=1000)

    deleted_player = player_service.delete_player(db=MagicMock(), player_id=1)

    assert deleted_player.id == 1
    assert deleted_player.name == "Maria da Silva"
    assert deleted_player.balance == 1000

def test_get_players(player_service, mock_player_repository):
    mock_player_repository.get_players.return_value = [
        PlayerResponse(id=1, name="Maria da Silva", balance=1000),
        PlayerResponse(id=2, name="Jane Doe", balance=2000)
    ]

    players = player_service.get_players(db=MagicMock())

    assert len(players) == 2
    assert players[0].id == 1
    assert players[0].name == "Maria da Silva"
    assert players[0].balance == 1000
    assert players[1].id == 2
    assert players[1].name == "Jane Doe"
    assert players[1].balance == 2000

def test_get_player_not_found(player_service, mock_player_repository):
    mock_player_repository.get_player.side_effect = PlayerNotFoundException(player_id=1)

    with pytest.raises(PlayerNotFoundException):
        player_service.get_player(db=MagicMock(), player_id=1)
