from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from enum import Enum

class ReportPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class ReportRequest(BaseModel):
    start_date: date
    end_date: date
    period: ReportPeriod
    user_id: Optional[int] = None  # If None, report for all family members

class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net: float
    categories: Dict[str, float]
    
class UserSummary(BaseModel):
    user_id: int
    user_name: str
    transactions: TransactionSummary

class PeriodSummary(BaseModel):
    period: str  # e.g., "2023-01-01" for daily, "2023-W01" for weekly, "2023-01" for monthly
    total_income: float
    total_expenses: float
    net: float

class Report(BaseModel):
    start_date: date
    end_date: date
    period: ReportPeriod
    overall: TransactionSummary
    by_user: List[UserSummary]
    by_period: List[PeriodSummary]
    generated_at: datetime
