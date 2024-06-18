from fastapi import HTTPException

class TransactionNotFoundException(HTTPException):
    def __init__(self, txn_uuid: str):
        super().__init__(
            status_code=404, 
            detail=f"Transaction with UUID {txn_uuid} not found."
            )
