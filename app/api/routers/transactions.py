from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.transaction import TransactionType, TransactionCategory
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/transactions/", response_model=Transaction)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new transaction.
    """
    transaction_service = TransactionService(db)
    notification_service = NotificationService(db)
    
    # Create the transaction
    transaction = transaction_service.create(
        obj_in=transaction_in, user_id=current_user.id
    )
    
    # Check if we need to send budget notifications
    if transaction.type == TransactionType.EXPENSE:
        notification_service.check_budget_thresholds(user_id=current_user.id)
    
    return transaction

@router.get("/transactions/", response_model=List[Transaction])
def read_transactions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[TransactionType] = None,
    category: Optional[TransactionCategory] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve transactions.
    """
    transaction_service = TransactionService(db)
    return transaction_service.get_multi(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        category=category,
    )

@router.get("/transactions/{transaction_id}", response_model=Transaction)
def read_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get specific transaction by ID.
    """
    transaction_service = TransactionService(db)
    transaction = transaction_service.get(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return transaction

@router.put("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    transaction_in: TransactionUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a transaction.
    """
    transaction_service = TransactionService(db)
    transaction = transaction_service.get(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    transaction = transaction_service.update(db_obj=transaction, obj_in=transaction_in)
    return transaction

@router.delete("/transactions/{transaction_id}", response_model=Transaction)
def delete_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a transaction.
    """
    transaction_service = TransactionService(db)
    transaction = transaction_service.get(id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    transaction = transaction_service.remove(id=transaction_id)
    return transaction
