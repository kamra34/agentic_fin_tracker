from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.schemas import TransactionCreate, TransactionUpdate
from typing import List, Optional
from datetime import datetime

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: TransactionCreate) -> Transaction:
        db_transaction = Transaction(**transaction.model_dump())
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def get_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.db.query(Transaction).order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def update_transaction(self, transaction_id: int, transaction_update: TransactionUpdate) -> Optional[Transaction]:
        db_transaction = self.get_transaction_by_id(transaction_id)
        if not db_transaction:
            return None

        update_data = transaction_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_transaction, field, value)

        db_transaction.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        db_transaction = self.get_transaction_by_id(transaction_id)
        if not db_transaction:
            return False

        self.db.delete(db_transaction)
        self.db.commit()
        return True
