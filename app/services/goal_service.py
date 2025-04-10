from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.goal import Goal, GoalContribution
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate

class GoalService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, id: int) -> Optional[Goal]:
        return self.db.query(Goal).filter(Goal.id == id).first()

    def get_user_goals(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Goal]:
        """Get goals where user is creator or participant"""
        return self.db.query(Goal).filter(
            (Goal.creator_id == user_id) | 
            (Goal.participants.any(User.id == user_id))
        ).order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()
        
    def get_family_goals(self, family_head_id: int, skip: int = 0, limit: int = 100) -> List[Goal]:
        """Get all goals for a family"""
        # Get all family members including head
        family_members = self.db.query(User).filter(
            (User.id == family_head_id) | (User.family_head_id == family_head_id)
        ).all()
        
        family_member_ids = [member.id for member in family_members]
        
        return self.db.query(Goal).filter(
            Goal.creator_id.in_(family_member_ids)
        ).order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, obj_in: GoalCreate, creator_id: int) -> Goal:
        # Create the goal
        db_obj = Goal(
            title=obj_in.title,
            description=obj_in.description,
            target_amount=obj_in.target_amount,
            current_amount=0.0,
            deadline=obj_in.deadline,
            is_completed=False,
            creator_id=creator_id,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        # Add participants
        participants = self.db.query(User).filter(User.id.in_(obj_in.participant_ids)).all()
        db_obj.participants = participants
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return db_obj

    def update(self, db_obj: Goal, obj_in: Union[GoalUpdate, Dict[str, Any]]) -> Goal:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Handle participant_ids separately
        participant_ids = update_data.pop("participant_ids", None)
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        # Update participants if provided
        if participant_ids is not None:
            participants = self.db.query(User).filter(User.id.in_(participant_ids)).all()
            db_obj.participants = participants
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def add_contribution(self, goal_id: int, user_id: int, amount: float) -> GoalContribution:
        """Add a contribution to a goal"""
        # Create contribution
        contribution = GoalContribution(
            amount=amount,
            goal_id=goal_id,
            user_id=user_id,
        )
        self.db.add(contribution)
        
        # Update goal current amount
        goal = self.get(id=goal_id)
        goal.current_amount += amount
        self.db.add(goal)
        
        self.db.commit()
        self.db.refresh(contribution)
        return contribution

    def mark_as_completed(self, goal_id: int) -> Goal:
        """Mark a goal as completed"""
        goal = self.get(id=goal_id)
        goal.is_completed = True
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal
        
    def get_goal_contributions(self, goal_id: int) -> List[GoalContribution]:
        """Get all contributions for a goal"""
        return self.db.query(GoalContribution).filter(
            GoalContribution.goal_id == goal_id
        ).order_by(GoalContribution.date.desc()).all()
        
    def get_user_contributions(self, user_id: int) -> List[GoalContribution]:
        """Get all contributions made by a user"""
        return self.db.query(GoalContribution).filter(
            GoalContribution.user_id == user_id
        ).order_by(GoalContribution.date.desc()).all()
        
    def get_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Get progress details for a goal"""
        goal = self.get(id=goal_id)
        if not goal:
            return None
            
        progress = {
            "goal_id": goal.id,
            "title": goal.title,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "is_completed": goal.is_completed,
            "progress_percentage": (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0,
            "remaining_amount": max(0, goal.target_amount - goal.current_amount),
            "deadline": goal.deadline,
            "days_remaining": None
        }
        
        # Calculate days remaining if deadline exists
        if goal.deadline:
            now = datetime.now()
            if goal.deadline > now:
                delta = goal.deadline - now
                progress["days_remaining"] = delta.days
            else:
                progress["days_remaining"] = 0
                
        return progress
