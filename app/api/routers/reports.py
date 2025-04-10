from typing import Any, List, Dict, Optional
from datetime import date, datetime, timedelta
import calendar

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import Report, ReportRequest
from app.services.report_service import ReportService

router = APIRouter()

@router.post("/reports/generate", response_model=Report)
def generate_report(
    *,
    db: Session = Depends(get_db),
    report_request: ReportRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate a financial report.
    """
    report_service = ReportService(db)
    
    # If user_id is specified, check permissions
    if report_request.user_id:
        if report_request.user_id != current_user.id:
            # Only family head can see reports for other family members
            if not current_user.is_family_head:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            # Check if the requested user is a family member
            user = db.query(User).filter(User.id == report_request.user_id).first()
            if not user or user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Generate report
    return report_service.generate_report(
        start_date=report_request.start_date,
        end_date=report_request.end_date,
        period=report_request.period,
        user_id=report_request.user_id or current_user.id,
        is_family_head=current_user.is_family_head
    )

@router.get("/reports/categories")
def get_category_report(
    *,
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    user_id: Optional[int] = Query(None, description="User ID (only for family head)"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Dict[str, float]]:
    """
    Get expense and income breakdown by category.
    """
    report_service = ReportService(db)
    
    # Determine which user(s) to include
    user_ids = []
    if user_id:
        # Check permissions
        if user_id != current_user.id:
            if not current_user.is_family_head:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        
        user_ids = [user_id]
    elif current_user.is_family_head:
        # Get all family members
        family_members = db.query(User).filter(
            (User.id == current_user.id) | (User.family_head_id == current_user.id)
        ).all()
        user_ids = [member.id for member in family_members]
    else:
        user_ids = [current_user.id]
    
    return report_service.get_category_report(user_ids, start_date, end_date)

@router.get("/reports/top-expenses")
def get_top_expenses(
    *,
    db: Session = Depends(get_db),
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(5, description="Number of top expenses to return"),
    user_id: Optional[int] = Query(None, description="User ID (only for family head)"),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get top expenses in the given period.
    """
    report_service = ReportService(db)
    
    # Determine which user(s) to include
    user_ids = []
    if user_id:
        # Check permissions
        if user_id != current_user.id:
            if not current_user.is_family_head:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        
        user_ids = [user_id]
    elif current_user.is_family_head:
        # Get all family members
        family_members = db.query(User).filter(
            (User.id == current_user.id) | (User.family_head_id == current_user.id)
        ).all()
        user_ids = [member.id for member in family_members]
    else:
        user_ids = [current_user.id]
    
    return report_service.get_top_expenses(user_ids, start_date, end_date, limit)

@router.get("/reports/goals")
def get_goal_progress_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get progress report for all family goals.
    """
    report_service = ReportService(db)
    
    # Only family head can see all goals
    if current_user.is_family_head:
        return report_service.get_goal_progress_report(current_user.id)
    else:
        # Regular users can only see their own goals
        family_head_id = current_user.family_head_id
        if not family_head_id:
            raise HTTPException(status_code=400, detail="User is not part of a family")
        
        # Filter goals to only include those where user is a participant
        all_goals = report_service.get_goal_progress_report(family_head_id)
        user_goals = [
            goal for goal in all_goals 
            if current_user.id in goal["participants"] or goal["creator_id"] == current_user.id
        ]
        
        return user_goals

@router.get("/reports/spending-trends")
def get_spending_trends(
    *,
    db: Session = Depends(get_db),
    months: int = Query(6, description="Number of months to include"),
    user_id: Optional[int] = Query(None, description="User ID (only for family head)"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get spending trends over time.
    """
    report_service = ReportService(db)
    
    # Determine which user to include
    target_user_id = current_user.id
    if user_id:
        # Check permissions
        if user_id != current_user.id:
            if not current_user.is_family_head:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        
        target_user_id = user_id
    
    return report_service.get_user_spending_trends(target_user_id, months)

@router.get("/reports/monthly-summary")
def get_monthly_summary(
    *,
    db: Session = Depends(get_db),
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month (1-12)"),
    user_id: Optional[int] = Query(None, description="User ID (only for family head)"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get monthly summary for a specific month.
    """
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Calculate start and end dates
    start_date = date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = date(year, month, last_day)
    
    report_service = ReportService(db)
    
    # Determine which user(s) to include
    user_ids = []
    if user_id:
        # Check permissions
        if user_id != current_user.id:
            if not current_user.is_family_head:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user or user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        
        user_ids = [user_id]
    elif current_user.is_family_head:
        # Get all family members
        family_members = db.query(User).filter(
            (User.id == current_user.id) | (User.family_head_id == current_user.id)
        ).all()
        user_ids = [member.id for member in family_members]
    else:
        user_ids = [current_user.id]
    
    # Get category breakdown
    categories = report_service.get_category_report(user_ids, start_date, end_date)
    
    # Get top expenses
    top_expenses = report_service.get_top_expenses(user_ids, start_date, end_date, 5)
    
    # Calculate overall summary
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    summary = report_service._calculate_transaction_summary(
        start_datetime, end_datetime, user_ids
    )
    
    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "summary": summary,
        "categories": categories,
        "top_expenses": top_expenses
    }
