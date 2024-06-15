from pydantic import UUID4
from sqlalchemy.orm import Session
from app.schemas.player_schema import PlayerResponse, PlayerCreate, PlayerUpdateResponse, PlayerUpdateRequest
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from app.repositories.player_repository import PlayerRepository
from typing import List

class PlayerService:
    def __init__(self, player_repository: PlayerRepository):
        self.player_repository = player_repository

    def create_player(self, db: Session, player: PlayerCreate) -> PlayerResponse:
        return self.player_repository.create_player(db=db, player=player)

    def get_player(self, db: Session, player_id: int) -> PlayerResponse:
        player = self.player_repository.get_player(db=db, player_id=player_id)
        if not player:
            raise PlayerNotFoundException(player_id)
        return player

    def get_players(self, db: Session) -> List[PlayerResponse]:
            players = self.player_repository.get_players(db=db)
            return [PlayerResponse(id=player.id, name=player.name, balance=player.balance) for player in players]
    
    def delete_player(self, db: Session, player_id: int) -> PlayerResponse:
        player = self.player_repository.delete_player(db=db, player_id=player_id)
        if not player:
            raise PlayerNotFoundException(player_id)
        return player
    
    def update_player(self, db: Session, player_id: int, player: PlayerUpdateRequest) -> PlayerUpdateResponse:
        db_player = self.player_repository.get_player(db=db, player_id=player_id)
        if not db_player:
            raise PlayerNotFoundException(player_id=player_id)

        updated_player = self.player_repository.update_player(db=db, player_id=player_id, player=player)
        return updated_player


    def log_transaction(self, db: Session, player_id: int, balance: float, txn_uuid: UUID4) -> None:
        player = self.player_repository.get_player(db=db, player_id=player_id)
        player.balance = balance
        self.player_repository.update_player(db=db, player=player)