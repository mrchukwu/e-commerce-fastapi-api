from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate
from app.modules.products.service import ProductService
from app.modules.users.model import User
from app.modules.users.schemas import UserRole

router = APIRouter()

@router.post("/", response_model=ProductRead)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create products")
  service = ProductService(db)
  response = service.create_product(payload)
  return response

@router.get("/", response_model=dict)
def list_products(
  page: int  = Query(default=1, ge=1),
  limit: int = Query(default=10, le=100),
  category_id: int | None = Query(default=None, ge=1),
  brand_name: str | None = Query(default=None, min_length=1),
  is_active: bool | None = Query(default=None),
  min_price: float | None = Query(default=None, ge=0.0),
  max_price: float | None = Query(default=None, ge=0.0),
  sort_price : str | None = Query(default=None, pattern=r"^(asc|desc)$", case_sensitive=False),
  db: Session = Depends(get_db)
  ):
  service = ProductService(db)
  response = service.list_products(
    page,
    limit,
    category_id,
    brand_name,
    is_active,
    min_price,
    max_price,
    sort_price
    )
  return {
    "data": response["data"],
    "pagination": {
      "page": response["pagination"]["page"],
      "limit": response["pagination"]["limit"],
      "total": response["pagination"]["total"],
      "total_pages": response["pagination"]["total_pages"]
    }
  }

@router.get("/search", response_model=dict)
def search_products(
  query: str = Query(..., min_length=1), 
  db: Session = Depends(get_db)
  ):
  service = ProductService(db)
  response = service.search_product(query)
  return {
    "data": response,
    "message": "Products found successfully"
  }

@router.get("/{product_id}", response_model=ProductRead)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
  service = ProductService(db)
  response = service.get_product(product_id)
  return response

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ProductRead:
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can create products")
  service = ProductService(db)
  response = service.update_product(product_id, payload)
  return response

@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
  if current_user.role != UserRole.ADMIN.value:
    raise HTTPException(
      status_code = status.HTTP_403_FORBIDDEN,
      detail = "only admin can delete products"
    )
  service = ProductService(db)
  service.delete_product(product_id)
  return {
    "message": "Product deleted successfully"
  }

