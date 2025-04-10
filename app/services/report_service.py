from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
import calendar

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, desc

from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.user import User
from app.models.goal import Goal, GoalContribution
from app.schemas.report import Report, ReportPeriod, TransactionSummary, UserSummary, PeriodSummary

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def generate_report(
        self,
        start_date: date,
        end_date: date,
        period: ReportPeriod,
        user_id: int,
        is_family_head: bool
    ) -> Report:
        """Generate a financial report"""
        # Convert dates to datetime for querying
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get users to include in report
        users = []
        if is_family_head:
            # Family head can see reports for all family members
            users = self.db.query(User).filter(
                (User.id == user_id) | (User.family_head_id == user_id)
            ).all()
        else:
            # Regular user can only see their own reports
            users = [self.db.query(User).filter(User.id == user_id).first()]
        
        # Calculate overall summary
        overall_summary = self._calculate_transaction_summary(
            start_datetime, end_datetime, [u.id for u in users]
        )
        
        # Calculate summary by user
        user_summaries = []
        for user in users:
            user_summary = self._calculate_transaction_summary(
                start_datetime, end_datetime, [user.id]
            )
            user_summaries.append(
                UserSummary(
                    user_id=user.id,
                    user_name=user.full_name,
                    transactions=user_summary
                )
            )
        
        # Calculate summary by period
        period_summaries = self._calculate_period_summaries(
            start_date, end_date, period, [u.id for u in users]
        )
        
        # Create and return the report
        return Report(
            start_date=start_date,
            end_date=end_date,
            period=period,
            overall=overall_summary,
            by_user=user_summaries,
            by_period=period_summaries,
            generated_at=datetime.now()
        )

    def _calculate_transaction_summary(
        self, start_date: datetime, end_date: datetime, user_ids: List[int]
    ) -> TransactionSummary:
        """Calculate transaction summary for given users and date range"""
        # Get total income
        total_income = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0
        
        # Get total expenses
        total_expenses = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).scalar() or 0.0
        
        # Get expenses by category
        categories = {}
        category_expenses = self.db.query(
            Transaction.category, func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.category).all()
        
        for category, amount in category_expenses:
            categories[category.value] = amount
        
        return TransactionSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            net=total_income - total_expenses,
            categories=categories
        )

    def _calculate_period_summaries(
        self, start_date: date, end_date: date, period: ReportPeriod, user_ids: List[int]
    ) -> List[PeriodSummary]:
        """Calculate summaries for each period in the date range"""
        period_summaries = []
        
        if period == ReportPeriod.DAILY:
            # Daily summaries
            current_date = start_date
            while current_date <= end_date:
                start_datetime = datetime.combine(current_date, datetime.min.time())
                end_datetime = datetime.combine(current_date, datetime.max.time())
                
                income = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.INCOME,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                expenses = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                period_summaries.append(
                    PeriodSummary(
                        period=current_date.isoformat(),
                        total_income=income,
                        total_expenses=expenses,
                        net=income - expenses
                    )
                )
                
                current_date += timedelta(days=1)
                
        elif period == ReportPeriod.WEEKLY:
            # Weekly summaries
            current_date = start_date
            while current_date <= end_date:
                # Calculate the start and end of the week
                week_start = current_date - timedelta(days=current_date.weekday())
                week_end = week_start + timedelta(days=6)
                
                # Adjust if outside the requested range
                if week_start < start_date:
                    week_start = start_date
                if week_end > end_date:
                    week_end = end_date
                
                start_datetime = datetime.combine(week_start, datetime.min.time())
                end_datetime = datetime.combine(week_end, datetime.max.time())
                
                income = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.INCOME,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                expenses = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                period_summaries.append(
                    PeriodSummary(
                        period=f"{week_start.isocalendar()[0]}-W{week_start.isocalendar()[1]}",
                        total_income=income,
                        total_expenses=expenses,
                        net=income - expenses
                    )
                )
                
                # Move to next week
                current_date = week_end + timedelta(days=1)
                
        elif period == ReportPeriod.MONTHLY:
            # Monthly summaries
            current_year = start_date.year
            current_month = start_date.month
            
            while (current_year < end_date.year or 
                  (current_year == end_date.year and current_month <= end_date.month)):
                
                # Calculate month start and end
                month_start = date(current_year, current_month, 1)
                _, last_day = calendar.monthrange(current_year, current_month)
                month_end = date(current_year, current_month, last_day)
                
                # Adjust if outside the requested range
                if month_start < start_date:
                    month_start = start_date
                if month_end > end_date:
                    month_end = end_date
                
                start_datetime = datetime.combine(month_start, datetime.min.time())
                end_datetime = datetime.combine(month_end, datetime.max.time())
                
                income = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.INCOME,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                expenses = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                period_summaries.append(
                    PeriodSummary(
                        period=f"{current_year}-{current_month:02d}",
                        total_income=income,
                        total_expenses=expenses,
                        net=income - expenses
                    )
                )
                
                # Move to next month
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
        
        elif period == ReportPeriod.YEARLY:
            # Yearly summaries
            current_year = start_date.year
            
            while current_year <= end_date.year:
                # Calculate year start and end
                year_start = date(current_year, 1, 1)
                year_end = date(current_year, 12, 31)
                
                # Adjust if outside the requested range
                if year_start < start_date:
                    year_start = start_date
                if year_end > end_date:
                    year_end = end_date
                
                start_datetime = datetime.combine(year_start, datetime.min.time())
                end_datetime = datetime.combine(year_end, datetime.max.time())
                
                income = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.INCOME,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                expenses = self.db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id.in_(user_ids),
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.date >= start_datetime,
                    Transaction.date <= end_datetime
                ).scalar() or 0.0
                
                period_summaries.append(
                    PeriodSummary(
                        period=str(current_year),
                        total_income=income,
                        total_expenses=expenses,
                        net=income - expenses
                    )
                )
                
                # Move to next year
                current_year += 1
        
        return period_summaries
        
    def get_category_report(self, user_ids: List[int], start_date: date, end_date: date) -> Dict[str, Dict[str, float]]:
        """Get expense breakdown by category"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get expenses by category
        category_expenses = self.db.query(
            Transaction.category, func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_datetime,
            Transaction.date <= end_datetime
        ).group_by(Transaction.category).all()
        
        # Get income by category
        category_income = self.db.query(
            Transaction.category, func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_datetime,
            Transaction.date <= end_datetime
        ).group_by(Transaction.category).all()
        
        result = {
            "expenses": {},
            "income": {}
        }
        
        for category, amount in category_expenses:
            result["expenses"][category.value] = amount
            
        for category, amount in category_income:
            result["income"][category.value] = amount
            
        return result
        
    def get_top_expenses(self, user_ids: List[int], start_date: date, end_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top expenses in the given period"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        top_expenses = self.db.query(Transaction).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_datetime,
            Transaction.date <= end_datetime
        ).order_by(Transaction.amount.desc()).limit(limit).all()
        
        result = []
        for expense in top_expenses:
            user = self.db.query(User).filter(User.id == expense.user_id).first()
            result.append({
                "id": expense.id,
                "amount": expense.amount,
                "description": expense.description,
                "category": expense.category.value,
                "date": expense.date,
                "user_id": expense.user_id,
                "user_name": user.full_name if user else "Unknown"
            })
            
        return result
        
    def get_goal_progress_report(self, family_head_id: int) -> List[Dict[str, Any]]:
        """Get progress report for all family goals"""
        # Get all family members including head
        family_members = self.db.query(User).filter(
            (User.id == family_head_id) | (User.family_head_id == family_head_id)
        ).all()
        
        family_member_ids = [member.id for member in family_members]
        
        # Get all goals
        goals = self.db.query(Goal).filter(
            Goal.creator_id.in_(family_member_ids)
        ).all()
        
        result = []
        for goal in goals:
            # Get creator
            creator = self.db.query(User).filter(User.id == goal.creator_id).first()
            
            # Get contributions
            contributions = self.db.query(GoalContribution).filter(
                GoalContribution.goal_id == goal.id
            ).all()
            
            # Calculate progress
            progress_percentage = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
            
            # Get days remaining
            days_remaining = None
            if goal.deadline:
                now = datetime.now()
                if goal.deadline > now:
                    delta = goal.deadline - now
                    days_remaining = delta.days
                else:
                    days_remaining = 0
            
            result.append({
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "remaining_amount": max(0, goal.target_amount - goal.current_amount),
                "progress_percentage": progress_percentage,
                "is_completed": goal.is_completed,
                "deadline": goal.deadline,
                "days_remaining": days_remaining,
                "creator_id": goal.creator_id,
                "creator_name": creator.full_name if creator else "Unknown",
                "created_at": goal.created_at,
                "contribution_count": len(contributions),
                "participants": [p.id for p in goal.participants]
            })
            
        return result
        
    def get_user_spending_trends(self, user_id: int, months: int = 6) -> Dict[str, List[Dict[str, Any]]]:
        """Get spending trends for a user over the last X months"""
        now = datetime.now()
        
        # Calculate start date (X months ago)
        if now.month <= months:
            start_year = now.year - 1
            start_month = 12 - (months - now.month)
        else:
            start_year = now.year
            start_month = now.month - months
            
        start_date = date(start_year, start_month, 1)
        end_date = date(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
        
        # Get monthly data
        monthly_data = []
        current_year = start_year
        current_month = start_month
        
        while (current_year < now.year or 
              (current_year == now.year and current_month <= now.month)):
            
            # Calculate month start and end
            month_start = date(current_year, current_month, 1)
            _, last_day = calendar.monthrange(current_year, current_month)
            month_end = date(current_year, current_month, last_day)
            
            start_datetime = datetime.combine(month_start, datetime.min.time())
            end_datetime = datetime.combine(month_end, datetime.max.time())
            
            # Get income
            income = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.date >= start_datetime,
                Transaction.date <= end_datetime
            ).scalar() or 0.0
            
            # Get expenses
            expenses = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_datetime,
                Transaction.date <= end_datetime
            ).scalar() or 0.0
            
            # Get expenses by category
            category_expenses = {}
            categories = self.db.query(
                Transaction.category, func.sum(Transaction.amount)
            ).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_datetime,
                Transaction.date <= end_datetime
            ).group_by(Transaction.category).all()
            
            for category, amount in categories:
                category_expenses[category.value] = amount
            
            monthly_data.append({
                "year": current_year,
                "month": current_month,
                "month_name": calendar.month_name[current_month],
                "income": income,
                "expenses": expenses,
                "net": income - expenses,
                "categories": category_expenses
            })
            
            # Move to next month
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
                
        return {
            "user_id": user_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "monthly_data": monthly_data
        }
