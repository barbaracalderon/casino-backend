from sqlalchemy.orm import Session
from app.models.transaction_model import Transaction
from app.schemas.transaction_schema import TransactionCreate
from app.exceptions.transaction_not_found_exception import TransactionNotFoundException
import logging


class TransactionRepository:
    def create_transaction(self, db: Session, transaction: TransactionCreate) -> Transaction:
        db_transaction = Transaction(**transaction.dict())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    

    def get_transaction(self, db: Session, transaction_id: int) -> Transaction:
        db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not db_transaction:
            raise TransactionNotFoundException(transaction_id)
        return db_transaction
    

    def get_transactions(self, db: Session):
        return db.query(Transaction).all()


    def delete_transaction(self, db: Session, transaction_id: int) -> Transaction:
        db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not db_transaction:
            raise TransactionNotFoundException(transaction_id)
        db.delete(db_transaction)
        db.commit()
        return db_transaction
    
    def get_transaction_by_uuid(self, db: Session, txn_uuid: str) -> Transaction:
        db_transaction = db.query(Transaction).filter(Transaction.txn_uuid == txn_uuid).first()
        return db_transaction
