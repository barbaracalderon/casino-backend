from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.services.player_service import PlayerService
from app.schemas.player_schema import PlayerResponse
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from app.repositories.player_repository import PlayerRepository

router = APIRouter()

def get_player_service(db: Session = Depends(get_db_session)) -> PlayerService:
    return PlayerService(PlayerRepository())

player_service = get_player_service()


@router.get("", response_model=PlayerResponse, tags=["balance"])
def get_balance(player: int = Query(..., description="Player ID")):
    db = next(get_db_session())
    try:
        player = player_service.get_player(db=db, player_id=player)
    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    finally:
        db.close()
    return PlayerResponse(id=player.id, name=player.name, balance=player.balance)