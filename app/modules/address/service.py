
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.address.model import Address
from app.modules.address.repository import AddressRepository
from app.modules.address.schemas import AddressCreate, AddressRead, AddressUpdate
from app.modules.users.model import User


class AddressService:
  def __init__(self, db: Session) -> None:
    self.address_repository = AddressRepository(db)
  
  def _dump_address(self, address: Address) -> AddressRead:
    return AddressRead.model_validate(address)

  def list_my_addresses(self, current_user: User) -> list[AddressRead]:
    addresses = self.address_repository.get_by_user_id(current_user.id)
    return [self._dump_address(address) for address in addresses]


  def get_address_by_id(self, current_user: User, address_id: int) -> AddressRead:
    address = self.address_repository.get_by_id(address_id)
    if address is None or address.user_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="address not found")
    return self._dump_address(address)

  def create_address(self, current_user: User, payload: AddressCreate) -> AddressRead:
    if payload.is_default:
      self.address_repository.unset_default_for_user(current_user.id)
    
    address = Address(
      user_id=current_user.id,
      **payload.model_dump()
      
    )

    db_address = self.address_repository.create(address)
    return self._dump_address(db_address)
    
    
  def update_address(self, address_id: int, payload: AddressUpdate, current_user: User) -> AddressRead:
    address = self.address_repository.get_by_id(address_id)
    if address is None or address.user_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="address not found")
    
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "is_default" in changes and changes["is_default"] is True:
      self.address_repository.unset_default_for_user(current_user.id)

    for field_name, value in changes.items():
      setattr(address, field_name, value)
    
    updated_address = self.address_repository.update(address, changes)
    return self._dump_address(updated_address)
    

  def delete_address(self, address_id: int, current_user: User) -> None:
    address = self.address_repository.get_by_id(address_id)
    if address is None or address.user_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="address not found")
    
    self.address_repository.delete(address)
    