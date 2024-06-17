from fastapi import HTTPException

class InvalidWinException(HTTPException):
    def __init__(self, value_win: float):
        super().__init__(
            status_code=400, 
            detail=f"Win value of {value_win} is not valid."
            )
