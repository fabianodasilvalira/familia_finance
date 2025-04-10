from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification, NotificationType
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.notification import NotificationUpdate

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter(Notification.id == id).first()

    def get_user_notifications(
        self, user_id: int, skip: int = 0, limit: int = 100, unread_only: bool = False
    ) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def create_manual_notification(self, user_id: int, title: str, message: str) -> Notification:
        """Create a manual notification"""
        notification = Notification(
            title=title,
            message=message,
            type=NotificationType.MANUAL,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
        
    def create_family_notification(self, family_head_id: int, title: str, message: str) -> List[Notification]:
        """Create a notification for all family members"""
        # Get all family members including head
        family_members = self.db.query(User).filter(
            (User.id == family_head_id) | (User.family_head_id == family_head_id)
        ).all()
        
        notifications = []
        for member in family_members:
            notification = Notification(
                title=title,
                message=message,
                type=NotificationType.MANUAL,
                user_id=member.id,
            )
            self.db.add(notification)
            notifications.append(notification)
            
        self.db.commit()
        for notification in notifications:
            self.db.refresh(notification)
            
        return notifications

    def create_budget_warning_notification(self, user_id: int, percentage: float) -> Notification:
        """Create a budget warning notification"""
        notification = Notification(
            title="Alerta de Orçamento",
            message=f"Você já utilizou {percentage:.0%} do seu orçamento mensal.",
            type=NotificationType.BUDGET_WARNING,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def create_budget_critical_notification(self, user_id: int, percentage: float) -> Notification:
        """Create a budget critical notification"""
        notification = Notification(
            title="Alerta Crítico de Orçamento",
            message=f"Crítico: Você já utilizou {percentage:.0%} do seu orçamento mensal!",
            type=NotificationType.BUDGET_CRITICAL,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def create_goal_notification(self, user_id: int, goal_id: int, goal_title: str) -> Notification:
        """Create a notification for a new goal"""
        notification = Notification(
            title="Nova Meta Adicionada",
            message=f"Você foi adicionado a uma nova meta: {goal_title}",
            type=NotificationType.GOAL_CONTRIBUTION,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def create_goal_achieved_notification(self, user_id: int, goal_id: int, goal_title: str) -> Notification:
        """Create a notification for an achieved goal"""
        notification = Notification(
            title="Meta Alcançada! 🎉",
            message=f"Parabéns! A meta '{goal_title}' foi totalmente financiada.",
            type=NotificationType.GOAL_ACHIEVED,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
        
    def create_contribution_notification(self, user_id: int, contributor_name: str, goal_title: str, amount: float) -> Notification:
        """Create a notification for a contribution to a goal"""
        notification = Notification(
            title="Nova Contribuição para Meta",
            message=f"{contributor_name} contribuiu R${amount:.2f} para a meta '{goal_title}'.",
            type=NotificationType.GOAL_CONTRIBUTION,
            user_id=user_id,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def check_budget_thresholds(self, user_id: int) -> None:
        """Check if user has exceeded budget thresholds and send notifications"""
        # Get current month's data
        now = datetime.now()
        year, month = now.year, now.month
        
        # Calculate month start and end
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        # Get total income for the month
        total_income = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= month_start,
            Transaction.date < month_end
        ).with_entities(Transaction.amount).all()
        total_income = sum(amount for amount, in total_income) if total_income else 0
        
        # Get total expenses for the month
        total_expenses = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= month_start,
            Transaction.date < month_end
        ).with_entities(Transaction.amount).all()
        total_expenses = sum(amount for amount, in total_expenses) if total_expenses else 0
        
        # If no income, we can't calculate budget percentage
        if total_income == 0:
            return
        
        # Calculate percentage of budget used
        budget_percentage = total_expenses / total_income
        
        # Check thresholds and send notifications
        if budget_percentage >= settings.BUDGET_CRITICAL_THRESHOLD:
            # Check if we already sent a critical notification this month
            existing = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == NotificationType.BUDGET_CRITICAL,
                Notification.created_at >= month_start,
                Notification.created_at < month_end
            ).first()
            
            if not existing:
                self.create_budget_critical_notification(user_id, budget_percentage)
        
        elif budget_percentage >= settings.BUDGET_WARNING_THRESHOLD:
            # Check if we already sent a warning notification this month
            existing = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type == NotificationType.BUDGET_WARNING,
                Notification.created_at >= month_start,
                Notification.created_at < month_end
            ).first()
            
            if not existing:
                self.create_budget_warning_notification(user_id, budget_percentage)

    def update(self, db_obj: Notification, obj_in: Union[NotificationUpdate, Dict[str, Any]]) -> Notification:
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

    def remove(self, id: int) -> Notification:
        obj = self.db.query(Notification).get(id)
        self.db.delete(obj)
        self.db.commit()
        return obj
        
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        result = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return result
