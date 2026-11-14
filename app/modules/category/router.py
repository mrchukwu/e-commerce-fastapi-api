from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.category.schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.modules.category.service import CategoryService
from app.modules.users.model import User
from app.modules.users.schemas import UserRole

router = APIRouter()

@router.get("/", response_model=list[CategoryRead])
def list_catgeories(db: Session = Depends(get_db)) -> list[CategoryRead]:
  service = CategoryService(db)
  return service.list_categories()

@router.post("/", response_model=CategoryRead)
def create_category(
  payload : CategoryCreate, 
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)
):
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Only admin can create categories",
    )
  service = CategoryService(db)
  return service.create_category(payload)

@router.get("/{category_id}",response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
  service = CategoryService(db)
  return service.get_categry(category_id)

@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
  category_id: int, 
  payload: CategoryUpdate, 
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)):
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Only admin can update categories",
    )
  service = CategoryService(db)
  return service.update_category(category_id, payload)

@router.delete("/{category_id}")
def delete_category(
  category_id: int, 
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)):
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Only admin can delete categories",
    )
  service = CategoryService(db)
  return service.delete_category(category_id)

  