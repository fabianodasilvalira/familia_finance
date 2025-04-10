from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.goal import Goal, GoalCreate, GoalUpdate, GoalContribution, GoalContributionCreate
from app.services.goal_service import GoalService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/goals/", response_model=Goal)
def create_goal(
    *,
    db: Session = Depends(get_db),
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new goal.
    """
    goal_service = GoalService(db)
    notification_service = NotificationService(db)
    
    # Create the goal
    goal = goal_service.create(obj_in=goal_in, creator_id=current_user.id)
    
    # Send notifications to all participants
    for participant_id in goal_in.participant_ids:
        notification_service.create_goal_notification(
            user_id=participant_id,
            goal_id=goal.id,
            goal_title=goal.title
        )
    
    return goal

@router.get("/goals/", response_model=List[Goal])
def read_goals(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve goals.
    """
    goal_service = GoalService(db)
    return goal_service.get_user_goals(user_id=current_user.id, skip=skip, limit=limit)

@router.get("/goals/{goal_id}", response_model=Goal)
def read_goal(
    *,
    db: Session = Depends(get_db),
    goal_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get specific goal by ID.
    """
    goal_service = GoalService(db)
    goal = goal_service.get(id=goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Check if user is creator or participant
    if goal.creator_id != current_user.id and current_user.id not in [p.id for p in goal.participants]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return goal

@router.put("/goals/{goal_id}", response_model=Goal)
def update_goal(
    *,
    db: Session = Depends(get_db),
    goal_id: int,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a goal.
    """
    goal_service = GoalService(db)
    goal = goal_service.get(id=goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    goal = goal_service.update(db_obj=goal, obj_in=goal_in)
    return goal

@router.post("/goals/{goal_id}/contribute", response_model=GoalContribution)
def contribute_to_goal(
    *,
    db: Session = Depends(get_db),
    goal_id: int,
    contribution_in: GoalContributionCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Contribute to a goal.
    """
    goal_service = GoalService(db)
    notification_service = NotificationService(db)
    
    goal = goal_service.get(id=goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Check if user is a participant
    if current_user.id not in [p.id for p in goal.participants] and goal.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a participant in this goal")
    
    # Create contribution
    contribution = goal_service.add_contribution(
        goal_id=goal_id,
        user_id=current_user.id,
        amount=contribution_in.amount
    )
    
    # Check if goal is completed
    if goal.current_amount >= goal.target_amount:
        goal_service.mark_as_completed(goal_id=goal_id)
        
        # Notify all participants
        for participant in goal.participants:
            notification_service.create_goal_achieved_notification(
                user_id=participant.id,
                goal_id=goal.id,
                goal_title=goal.title
            )
    
    return contribution
