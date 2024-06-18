import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.services.transaction_service import TransactionService
from app.exceptions.transaction_not_found_exception import TransactionNotFoundException
from app.schemas.transaction_schema import (
    TransactionCreate,
)
from app.models.transaction_model import Transaction


@pytest.fixture
def mock_transaction_repository():
    return MagicMock()


@pytest.fixture
def transaction_service(mock_transaction_repository):
    return TransactionService(mock_transaction_repository)


def test_create_transaction(transaction_service, mock_transaction_repository):
    transaction_create_data = TransactionCreate(txn_uuid="1234", player_id=1, value_bet=100, value_win=50)
    mock_db_session = MagicMock(spec=Session)

    mock_transaction_repository.create_transaction.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50
    )

    created_transaction = transaction_service.create_transaction(db=mock_db_session, transaction=transaction_create_data)

    assert created_transaction.id == 1
    assert created_transaction.txn_uuid == "1234"
    assert created_transaction.player_id == 1
    assert created_transaction.value_bet == 100
    assert created_transaction.value_win == 50


def test_get_transaction(transaction_service, mock_transaction_repository):
    mock_transaction_repository.get_transaction.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50
    )

    found_transaction = transaction_service.get_transaction(db=MagicMock(), transaction_id=1)

    assert found_transaction.id == 1
    assert found_transaction.txn_uuid == "1234"
    assert found_transaction.player_id == 1
    assert found_transaction.value_bet == 100
    assert found_transaction.value_win == 50


def test_delete_transaction(transaction_service, mock_transaction_repository):
    mock_transaction_repository.delete_transaction.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50
    )

    deleted_transaction = transaction_service.delete_transaction(db=MagicMock(), transaction_id=1)

    assert deleted_transaction.id == 1
    assert deleted_transaction.txn_uuid == "1234"
    assert deleted_transaction.player_id == 1
    assert deleted_transaction.value_bet == 100
    assert deleted_transaction.value_win == 50


def test_get_transactions(transaction_service, mock_transaction_repository):
    mock_transaction_repository.get_transactions.return_value = [
        Transaction(id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50),
        Transaction(id=2, txn_uuid="5678", player_id=2, value_bet=200, value_win=150)
    ]

    transactions = transaction_service.get_transactions(db=MagicMock())

    assert len(transactions) == 2
    assert transactions[0].id == 1
    assert transactions[0].txn_uuid == "1234"
    assert transactions[0].player_id == 1
    assert transactions[0].value_bet == 100
    assert transactions[0].value_win == 50
    assert transactions[1].id == 2
    assert transactions[1].txn_uuid == "5678"
    assert transactions[1].player_id == 2
    assert transactions[1].value_bet == 200
    assert transactions[1].value_win == 150


def test_get_transaction_by_uuid_not_found(transaction_service, mock_transaction_repository):
    mock_transaction_repository.get_transaction_by_uuid.side_effect = TransactionNotFoundException(txn_uuid="aaa")

    with pytest.raises(TransactionNotFoundException):
        transaction_service.get_transaction_by_uuid(db=MagicMock(), txn_uuid="aaa")


def test_get_transaction_by_uuid(transaction_service, mock_transaction_repository):
    mock_transaction_repository.get_transaction_by_uuid.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50
    )

    found_transaction = transaction_service.get_transaction_by_uuid(db=MagicMock(), txn_uuid="1234")

    assert found_transaction.id == 1
    assert found_transaction.txn_uuid == "1234"
    assert found_transaction.player_id == 1
    assert found_transaction.value_bet == 100
    assert found_transaction.value_win == 50


def test_mark_transaction_rolled_back(transaction_service, mock_transaction_repository):
    mock_transaction_repository.mark_transaction_rolled_back.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50, rolled_back=True
    )

    rolled_back_transaction = transaction_service.mark_transaction_rolled_back(db=MagicMock(), txn_uuid="1234")

    assert rolled_back_transaction.id == 1
    assert rolled_back_transaction.txn_uuid == "1234"
    assert rolled_back_transaction.player_id == 1
    assert rolled_back_transaction.value_bet == 100
    assert rolled_back_transaction.value_win == 50
    assert rolled_back_transaction.rolled_back is True


def test_create_transaction_marked_rolledback(transaction_service, mock_transaction_repository):
    mock_transaction_repository.create_transaction_marked_rolledback.return_value = Transaction(
        id=1, txn_uuid="1234", player_id=1, value_bet=100, value_win=50, rolled_back=True
    )

    created_transaction = transaction_service.create_transaction_marked_rolledback(db=MagicMock(), transaction="1234")

    assert created_transaction.id == 1
    assert created_transaction.txn_uuid == "1234"
    assert created_transaction.player_id == 1
    assert created_transaction.value_bet == 100
    assert created_transaction.value_win == 50
    assert created_transaction.rolled_back is True
