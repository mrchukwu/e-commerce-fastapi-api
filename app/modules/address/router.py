
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.dependencies import get_current_user, get_db
from app.modules.address.schemas import AddressCreate, AddressRead, AddressUpdate
from app.modules.address.service import AddressService
from app.modules.users.model import User

router = APIRouter()

@router.get("/", response_model=list[AddressRead])
def list_my_addresses(
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = AddressService(db)
  return service.list_my_addresses(current_user)  

@router.post("/", response_model=AddressRead)
def create_address(
  payload: AddressCreate,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = AddressService(db)
  return service.create_address(current_user, payload)

@router.get("/{address_id}", response_model=AddressRead)
def get_address_by_id(
  address_id: int,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = AddressService(db)
  return service.get_address_by_id(current_user, address_id)  

@router.patch("/{address_id}", response_model=AddressRead)
def update_address(
  address_id: int,
  payload: AddressUpdate,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = AddressService(db)
  return service.update_address(address_id, payload, current_user)

@router.delete("/{address_id}", response_model=dict)
def delete_address(
  address_id: int,
  current_user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  service = AddressService(db)
  service.delete_address(address_id, current_user)
  return {
    "message": "Address deleted successfully"
  }