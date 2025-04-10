from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.transaction import TransactionType, TransactionCategory

# Shared properties
class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: str
    type: TransactionType
    category: TransactionCategory
    date: datetime

# Properties to receive via API on creation
class TransactionCreate(TransactionBase):
    pass

# Properties to receive via API on update
class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    category: Optional[TransactionCategory] = None
    date: Optional[datetime] = None

# Properties shared by models stored in DB
class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return via API
class Transaction(TransactionInDBBase):
    pass

# Properties stored in DB
class TransactionInDB(TransactionInDBBase):
    pass
