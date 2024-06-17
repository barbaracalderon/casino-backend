from fastapi import HTTPException

class InvalidBetException(HTTPException):
    def __init__(self, value_bet: float):
        super().__init__(
            status_code=400, 
            detail=f"Bet value of {value_bet} is not valid."
            )
