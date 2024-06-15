from sqlalchemy.orm import Session
from app.models.player_model import Player
from app.schemas.player_schema import PlayerCreate, PlayerUpdateRequest
from app.exceptions.player_not_found_exception import PlayerNotFoundException
import logging


class PlayerRepository:
    def create_player(self, db: Session, player: PlayerCreate) -> Player:
        db_player = Player(**player.dict())
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
        return db_player


    def get_player(self, db: Session, player_id: int) -> Player:
        db_player = db.query(Player).filter(Player.id == player_id).first()
        if not db_player:
            raise PlayerNotFoundException(player_id)
        return db_player


    def get_players(self, db: Session):
        return db.query(Player).all()


    def delete_player(self, db: Session, player_id: int) -> Player:
        db_player = db.query(Player).filter(Player.id == player_id).first()
        if not db_player:
            raise PlayerNotFoundException(player_id)
        db.delete(db_player)
        db.commit()
        return db_player


    def update_player(self, db: Session, player_id: int, player: PlayerUpdateRequest) -> Player:
        db_player = db.query(Player).filter(Player.id == player_id).first()
        if not db_player:
            raise PlayerNotFoundException(player_id=player_id)
        
        db_player.name = player.name
        db_player.balance = player.balance
       
        try:
            db.commit()
            db.refresh(db_player)
        except Exception as e:
            logging.error(f"Failed to update player {player_id}: {str(e)}")
            db.rollback()
            raise e
        
        return db_player

