from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == id).first()

    def get_multi(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None,
        category: Optional[TransactionCategory] = None,
    ) -> List[Transaction]:
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.date >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(Transaction.date <= datetime.combine(end_date, datetime.max.time()))
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if category:
            query = query.filter(Transaction.category == category)
        
        return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

    def create(self, obj_in: TransactionCreate, user_id: int) -> Transaction:
        db_obj = Transaction(
            amount=obj_in.amount,
            description=obj_in.description,
            type=obj_in.type,
            category=obj_in.category,
            date=obj_in.date,
            user_id=user_id,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Transaction, obj_in: Union[TransactionUpdate, Dict[str, Any]]) -> Transaction:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: int) -> Transaction:
        obj = self.db.query(Transaction).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj

    def get_monthly_totals(self, user_id: int, year: int, month: int) -> Dict[str, float]:
        """Get total income and expenses for a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).scalar() or 0.0
        
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).scalar() or 0.0
        
        return {
            "income": income,
            "expenses": expenses,
            "balance": income - expenses
        }
        
    def get_transactions_by_family(
        self,
        family_head_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[TransactionType] = None,
        category: Optional[TransactionCategory] = None,
    ) -> List[Transaction]:
        """Get transactions for all family members"""
        from app.models.user import User
        
        # Get all family members including head
        family_members = self.db.query(User).filter(
            (User.id == family_head_id) | (User.family_head_id == family_head_id)
        ).all()
        
        family_member_ids = [member.id for member in family_members]
        
        query = self.db.query(Transaction).filter(Transaction.user_id.in_(family_member_ids))
        
        if start_date:
            query = query.filter(Transaction.date >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(Transaction.date <= datetime.combine(end_date, datetime.max.time()))
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if category:
            query = query.filter(Transaction.category == category)
        
        return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
