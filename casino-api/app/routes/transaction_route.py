from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Union
from app.schemas.transaction_schema import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionsResponse, 
    TransactionBalanceResponse,
    TransactionWin,
    TransactionCancelled,
    TransactionBalanceUpdate
)
from app.schemas.player_schema import PlayerUpdateRequest
from app.services.transaction_service import TransactionService
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.player_repository import PlayerRepository
from app.services.player_service import PlayerService
from app.db import get_db_session
from app.exceptions.transaction_not_found_exception import TransactionNotFoundException
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from fastapi import HTTPException


router = APIRouter()


def get_transaction_service(db: Session = Depends(get_db_session)) -> TransactionService:
    return TransactionService(TransactionRepository())

def get_player_service(db: Session = Depends(get_db_session)) -> PlayerService:
    return PlayerService(PlayerRepository())

transaction_service = get_transaction_service()
player_service = get_player_service()

@router.post("/bet", response_model=TransactionBalanceResponse, status_code=200)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db_session)):
    transaction_service = get_transaction_service(db)
    player_service = get_player_service(db)

    existing_transaction = transaction_service.get_transaction_by_uuid(db, transaction.txn_uuid)
    existing_player = player_service.get_player(db=db, player_id=transaction.player_id)

    if existing_transaction:
        return TransactionBalanceResponse(
            id=existing_transaction.id,
            player_id=existing_player.id,
            balance=existing_player.balance,
            txn_uuid=existing_transaction.txn_uuid
        )

    try:
        db_player = player_service.get_player(db, transaction.player_id)
        if db_player.balance < transaction.value_bet:
            raise HTTPException(status_code=400, detail="Insufficient balance for this operation.")

        db_player.balance -= transaction.value_bet

        player_update = PlayerUpdateRequest(name=db_player.name, balance=db_player.balance)
        player_id = db_player.id

        player_service.update_player(db=db, player_id=player_id, player=player_update)

        db_transaction = transaction_service.create_transaction(db=db, transaction=transaction)

        return TransactionBalanceResponse(
            id=db_transaction.id,
            player_id=player_id,
            balance=player_update.balance,
            txn_uuid=db_transaction.txn_uuid
        )

    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))


@router.get("", response_model=TransactionsResponse)
def read_transactions(db: Session = Depends(get_db_session)):
    transactions = transaction_service.get_transactions(db=db)
    return TransactionsResponse(transactions=transactions)


@router.get("/{txn_uuid}", response_model=TransactionResponse)
def get_transaction_by_uuid(txn_uuid: str, db: Session = Depends(get_db_session)):
    try:
        transaction = transaction_service.get_transaction_by_uuid(db=db, txn_uuid=txn_uuid)
        if transaction is None:
            raise TransactionNotFoundException(txn_uuid=txn_uuid)
        
        return TransactionResponse(
            id=transaction.id,
            txn_uuid=transaction.txn_uuid,
            player_id=transaction.player_id,
            value_bet=transaction.value_bet,
            value_win=transaction.value_win
        )
    except TransactionNotFoundException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db_session)):
    try:
        transaction = transaction_service.delete_transaction(db=db, transaction_id=transaction_id)
        return transaction
    except TransactionNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
        

@router.post("/win", response_model=TransactionBalanceResponse, status_code=200)
def win_transaction(transaction: TransactionWin, db: Session = Depends(get_db_session)):
    transaction_service = get_transaction_service(db)
    player_service = get_player_service(db)

    existing_transaction = transaction_service.get_transaction_by_uuid(db, transaction.txn_uuid)
    existing_player = player_service.get_player(db=db, player_id=transaction.player_id)

    if existing_transaction:
        return TransactionBalanceResponse(
            id=existing_transaction.id,
            player_id=existing_player.id,
            balance=existing_player.balance,
            txn_uuid=existing_transaction.txn_uuid
        )

    try:
        db_player = player_service.get_player(db, transaction.player_id)

        db_player.balance += transaction.value_win

        player_update = PlayerUpdateRequest(name=db_player.name, balance=db_player.balance)
        player_id = db_player.id

        player_service.update_player(db=db, player_id=player_id, player=player_update)

        db_transaction = transaction_service.create_transaction(db=db, transaction=transaction)

        return TransactionBalanceResponse(
            id=db_transaction.id,
            player_id=player_id,
            balance=player_update.balance,
            txn_uuid=db_transaction.txn_uuid
        )

    except PlayerNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
    
