from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.cart.schemas import AddCartItemRequest, CartRead, UpdateCartItemRequest
from app.modules.cart.service import CartService
from app.modules.category.schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.modules.category.service import CategoryService
from app.modules.users.model import User
from app.modules.users.schemas import UserRole

router = APIRouter()


@router.get("/", response_model=CartRead)
def list_carts(db: Session = Depends(get_db)):
  service = CartService(db)
  return service.list_carts()

@router.post("/items", response_model=CartRead)
def add_item_to_cart(
  payload: AddCartItemRequest,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = CartService(db)
  return service.add_items(current_user, payload)

@router.get("/me", response_model=CartRead)
def get_my_cart(
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = CartService(db)
  return service.get_my_cart(current_user)

@router.delete("/clear", response_model=dict)
def clear_my_cart(
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = CartService(db)
  service.clear_cart(current_user)
  return {"message": "Cart cleared successfully"}

@router.patch("/items/{item_id}", response_model=CartRead)
def update_cart_item(
  item_id: int,
  payload: UpdateCartItemRequest,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = CartService(db)
  return service.update_item(current_user, item_id, payload)

@router.get("/{cart_id}", response_model=CartRead)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
  service = CartService(db)
  return service.get_cart(cart_id)

@router.delete("/items/{item_id}", response_model=CartRead)
def remove_cart_item(
  item_id: int,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = CartService(db)
  return service.remove_item(current_user, item_id)


