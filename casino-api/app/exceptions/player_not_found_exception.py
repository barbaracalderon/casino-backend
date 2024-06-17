from fastapi import HTTPException

class PlayerNotFoundException(HTTPException):
    def __init__(self, player_id: int):
        super().__init__(
            status_code=404, 
            detail=f"Player with id {player_id} not found."
            )
