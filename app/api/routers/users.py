from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_family_head, get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, FamilyMember
from app.services.user_service import UserService

router = APIRouter()

@router.get("/users/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/users/me", response_model=UserSchema)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update own user.
    """
    user_service = UserService(db)
    user = user_service.update(db_obj=current_user, obj_in=user_in)
    return user

@router.get("/users/family", response_model=List[FamilyMember])
def read_family_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve family members.
    """
    user_service = UserService(db)
    if current_user.is_family_head:
        return user_service.get_family_members(current_user.id)
    return user_service.get_family_members(current_user.family_head_id)

@router.post("/users/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_family_head),
) -> Any:
    """
    Create new user (family member).
    """
    user_service = UserService(db)
    user = user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Set family head ID if not provided
    if not user_in.family_head_id and not user_in.is_family_head:
        user_in.family_head_id = current_user.id
    
    return user_service.create(obj_in=user_in)

@router.get("/users/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user_service = UserService(db)
    user = user_service.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check if user is family head or trying to access a family member
    if current_user.id != user_id:
        if current_user.is_family_head:
            if user.family_head_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif current_user.family_head_id != user.family_head_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return user
