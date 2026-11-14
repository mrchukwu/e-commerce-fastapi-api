from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules import category
from app.modules.category.model import Category
from app.modules.category.repository import CategoryRepository
from app.modules.category.schema import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
  def __init__(self, db: Session) -> None:
    self.category_repository = CategoryRepository(db)
  
  def _dump_category(self, category: Category) -> CategoryRead:
    return CategoryRead.model_validate(category)

  
  def list_categories(self) -> list[CategoryRead]:
    categories = self.category_repository.get_all()
    return [self._dump_category(category) for category in categories]
  
  def get_categry(self, category_id: int) -> CategoryRead:
    categotry = self.category_repository.get_by_id(category_id)
    if not categotry:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Category not found"
      )
    return self._dump_category(categotry)

  
  def create_category(self, payload: CategoryCreate) -> CategoryRead:
    if payload.parent_id is not None:
      parent_catgory = self.category_repository.get_by_id(payload.parent_id)
      if parent_catgory is None:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND, 
          detail="Parent category not found"
        )
    db_category = Category(**payload.model_dump())
    saved_category = self.category_repository.create(db_category)
    return self._dump_category(saved_category)
    

  def update_category(self, category_id: int, payload: CategoryUpdate) -> CategoryRead:
    category = self.category_repository.get_by_id(category_id)
    if category is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Category not found"
      )
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "parent_id" in changes:
      parent_id = changes["parent_id"]
      if parent_id == category_id:
        raise HTTPException(
          status_code=status.HTTP_409_CONFLICT,
          detail="parent id cannot be same as category id"
        )
      if parent_id is not None:
        parent_category = self.category_repository.get_by_id(parent_id)
        if parent_category is None:
          raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent category not found",
          )
        if parent_category.is_active is False:
          raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent category is not active"
          )
    for field, value in changes.items():
      setattr(category, field, value)

    updated_category = self.category_repository.update(category)
    return self._dump_category(updated_category)    
    
  def delete_category(self, category_id: int) -> dict:
    category = self.category_repository.get_by_id(category_id)
    if not category:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Category not found"
      )
    self.category_repository.delete(category)
    return {
      "message": "Category deleted successfully"
    }