from sqlalchemy.orm import Session
from app.models.player_model import Player
from app.schemas.player_schema import PlayerCreate
from app.exceptions.player_not_found_exception import PlayerNotFoundException

class PlayerRepository:
    def create_player(self, db: Session, player: PlayerCreate) -> Player:
        db_player = Player(**player.dict())
        db.add(db_player)
        db.commit()
        db.refresh(db_player)
        return db_player

    def get_player(self, db: Session, player_id: int) -> Player:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise PlayerNotFoundException(player_id)
        return player

    def get_players(self, db: Session):
        return db.query(Player).all()

    def delete_player(self, db: Session, player_id: int) -> Player:
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise PlayerNotFoundException(player_id)
        db.delete(player)
        db.commit()
        return player
