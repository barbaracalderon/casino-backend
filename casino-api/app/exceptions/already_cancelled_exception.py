from fastapi import HTTPException

class AlreadyCancelledException(HTTPException):
    def __init__(self, txn_uuid: str):
        super().__init__(
            status_code=400, 
            detail=f"Error while processing. The transaction {txn_uuid} is already cancelled (rolled_back)."
            )
