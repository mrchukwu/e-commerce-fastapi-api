from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.address import service
from app.modules.cart.service import CartService
from app.modules.category.schema import CategoryCreate, CategoryRead, CategoryUpdate
from app.modules.category.service import CategoryService
from app.modules.order.schemas import OrderRead, OrderStatusUpdate, PlaceOrderRequest
from app.modules.order.service import OrderService
from app.modules.users.model import User
from app.modules.users.schemas import UserRole

router = APIRouter()


@router.get("/me", response_model=list[OrderRead])
def list_my_orders(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    service = OrderService(db)
    return service.list_my_order(current_user)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= OrderRead)
def place_order(payload: PlaceOrderRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
  service = OrderService(db)
  order = service.place_order(current_user, payload)
  return order

@router.get("/", response_model = list[OrderRead])
def list_my_orders(
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)
):
  service = OrderService(db)
  return service.list_all_orders(current_user)

@router.get("/{order_id}", response_model = OrderRead)
def get_order_by_id(
  order_id: int,
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)
):
  service = OrderService(db)
  return service.get_order(order_id)


@router.patch("/{order_id}", response_model = OrderRead)
def update_order_status(
  order_id: int,
  payload: OrderStatusUpdate,
  current_user: User = Depends(get_current_user), 
  db: Session = Depends(get_db)
):
  service = OrderService(db)
  return service.update_order_status(current_user, order_id, payload)

