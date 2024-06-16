from sqlalchemy.orm import Session
from typing import List, Union
from app.repositories.transaction_repository import TransactionRepository
from app.models.transaction_model import Transaction
from app.exceptions.transaction_not_found_exception import TransactionNotFoundException
from app.schemas.transaction_schema import (
    TransactionCreate,
    TransactionResponse,
    TransactionCancelled
)

class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository


    def create_transaction(self, db: Session, transaction: TransactionCreate) -> Transaction:
        return self.transaction_repository.create_transaction(db=db, transaction=transaction)


    def get_transaction(self, db: Session, transaction_id: int) -> Transaction:
        transaction = self.transaction_repository.get_transaction(db=db, transaction_id=transaction_id)
        if not transaction:
            raise TransactionNotFoundException(transaction_id)
        return transaction


    def get_transactions(self, db: Session) -> List[TransactionResponse]:
        transactions = self.transaction_repository.get_transactions(db=db)
        return [TransactionResponse(
            id=transaction.id, 
            txn_uuid=transaction.txn_uuid,
            player_id=transaction.player_id, 
            value_bet=transaction.value_bet if transaction.value_bet else 0,
            value_win=transaction.value_win if transaction.value_win else 0) for transaction in transactions]
        

    def delete_transaction(self, db: Session, transaction_id: int) -> TransactionResponse:
        transaction = self.transaction_repository.delete_transaction(db=db, transaction_id=transaction_id)
        if not transaction:
            raise TransactionNotFoundException(transaction_id)
        return transaction


    def get_transaction_by_uuid(self, db: Session, txn_uuid: str) -> Transaction:
        return self.transaction_repository.get_transaction_by_uuid(db=db, txn_uuid=txn_uuid)



    def store_cancellation_request(self, db: Session, transaction: TransactionCancelled):
        cancellation = TransactionCancelled(
            txn_uuid=transaction.reference_txn_uuid,
            player_id=transaction.player_id,
            value_bet=transaction.value
        )
        db.add(cancellation)
        db.commit()


    def check_cancellation_request(self, db: Session, txn_uuid: str):
        return db.query(TransactionCancelled).filter(TransactionCancelled.txn_uuid == txn_uuid).first()
