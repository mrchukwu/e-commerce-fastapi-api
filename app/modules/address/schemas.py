from pydantic import BaseModel, Field


class AddressBase(BaseModel):
  full_name: str
  phone_number: str
  address_line1: str
  address_line2: str | None = None
  city: str
  state: str
  postal_code: str
  country: str = "Nigeria"
  is_default: bool = False

class AddressCreate(AddressBase):
  pass

class AddressUpdate(BaseModel):
  full_name: str | None = None
  phone_number: str | None = None
  address_line1: str | None = None
  address_line2: str | None = None
  city: str | None = None
  state: str | None = None
  postal_code: str | None = None
  country: str | None = None
  is_defaut: bool | None = None

class AddressRead(AddressBase):
  id: int
  user_id: int

  class Config:
    from_attributes = True
