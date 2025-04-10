from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Shared properties
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    deadline: Optional[datetime] = None

# Properties to receive via API on creation
class GoalCreate(GoalBase):
    participant_ids: List[int]

# Properties to receive via API on update
class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    deadline: Optional[datetime] = None
    is_completed: Optional[bool] = None
    participant_ids: Optional[List[int]] = None

# Properties shared by models stored in DB
class GoalInDBBase(GoalBase):
    id: int
    current_amount: float
    is_completed: bool
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return via API
class Goal(GoalInDBBase):
    participants: List[int]  # List of participant IDs
    progress_percentage: float

# Properties stored in DB
class GoalInDB(GoalInDBBase):
    pass

# Contribution schemas
class GoalContributionBase(BaseModel):
    amount: float = Field(..., gt=0)
    goal_id: int

# Properties to receive via API on creation
class GoalContributionCreate(GoalContributionBase):
    pass

# Properties shared by models stored in DB
class GoalContributionInDBBase(GoalContributionBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        from_attributes = True

# Properties to return via API
class GoalContribution(GoalContributionInDBBase):
    pass
