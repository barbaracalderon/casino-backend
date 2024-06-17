from fastapi import HTTPException

class InvalidBalanceException(HTTPException):
    def __init__(self, balance: float):
        super().__init__(
            status_code=422, 
            detail=f"The balance value of {balance} is not valid. Only positive numbers or zero."
            )
