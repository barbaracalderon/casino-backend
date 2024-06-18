from fastapi import HTTPException

class InvalidBetException(HTTPException):
    def __init__(self, value_bet: float):
        super().__init__(
            status_code=422, 
            detail=f"Bet value must be positive, not {value_bet}."
            )
