from fastapi import HTTPException

class TransactionNotFoundException(HTTPException):
    def __init__(self, txn_uuid: str):
        self.status_code = 404
        self.detail = f"Transaction with UUID {txn_uuid} not found"
        super().__init__(status_code=404, detail=self.detail)
