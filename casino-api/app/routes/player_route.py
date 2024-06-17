from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db import get_db_session
from app.services.player_service import PlayerService
from app.schemas.player_schema import PlayerCreate
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from app.exceptions.invalid_balance_exception import InvalidBalanceException
from app.schemas.player_schema import (
    PlayerResponse, 
    PlayersResponse, 
    PlayerUpdateResponse, 
    PlayerUpdateRequest
)
from app.repositories.player_repository import PlayerRepository


router = APIRouter()

def get_player_service(db: Session = Depends(get_db_session)) -> PlayerService:
    return PlayerService(PlayerRepository())

player_service = get_player_service()


@router.post("", response_model=PlayerResponse, status_code=201)
def create_player(player: PlayerCreate, db: Session = Depends(get_db_session)):
    try:
        if player.balance < 0:
            raise InvalidBalanceException(balance=player.balance)
        return player_service.create_player(db=db, player=player)
    except InvalidBalanceException as e:
        raise HTTPException(status_code=e.status_code, detail=(str(e.detail)))


@router.get("", response_model=PlayersResponse)
def read_players(db: Session = Depends(get_db_session)):
    players = player_service.get_players(db=db)
    return PlayersResponse(players=players)


@router.get("/{player_id}", response_model=PlayerResponse)
def read_player(player_id: int, db: Session = Depends(get_db_session)):
    try:
        return player_service.get_player(db=db, player_id=player_id)
    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))


@router.delete("/{player_id}", response_model=PlayerResponse)
def delete_player(player_id: int, db: Session = Depends(get_db_session)):
    try:
        return player_service.delete_player(db=db, player_id=player_id)
    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    

@router.put("/{player_id}", response_model=PlayerUpdateResponse)
def update_player(player_id: int, player: PlayerUpdateRequest, db: Session = Depends(get_db_session)):
    player_service = get_player_service(db)
    try:
        updated_player = player_service.update_player(db=db, player_id=player_id, player=player)
        return updated_player
    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))