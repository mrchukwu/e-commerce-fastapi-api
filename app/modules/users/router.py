from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.users.model import User
from app.modules.users.schemas import UserRead, UserRole, UserUpdate
from app.modules.users.service import UserService

router = APIRouter() 

# /api/v1/users/

@router.get("/", response_model=list[UserRead])
def list_users(
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)
  ):

  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail="Only admin can access this resource"
    )
  service = UserService(db)
  users = service.list_users()
  return users

@router.get("/profile", response_model=UserRead)
def get_current_user_profile(
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = UserService(db)
  user = service.get_current_user(current_user)
  return user

@router.get("/{user_id}", response_model=UserRead)
def get_user(
  user_id:int,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
    service = UserService(db)
    user = service.get_user(user_id)
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    service = UserService(db)
    user = service.update_user(user_id, payload)
    return user

@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can access this resource"
        )
    service = UserService(db)
    user = service.delete_user(user_id)
    return {
      "message" : "User deleted successfully"
    }