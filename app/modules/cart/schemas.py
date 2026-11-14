from sys import float_repr_style
from pydantic import BaseModel, Field


class AddCartItemRequest(BaseModel):
  product_id: int = Field(gt=0)
  quantity: int = Field(default=1, ge=0)


class UpdateCartItemRequest(BaseModel):
  quantity: int = Field(gt=0)


class CardProductSummary(BaseModel):
  id: int 
  name: str
  discount_percent: float
  price: float
  selling_price: float
  image_url: str
  

class CartItemRead(BaseModel):
  id: int
  product_id: int
  quantity: int
  unit_price: float
  unit_selling_price: float
  subtotal: float
  product: CardProductSummary

class CartRead(BaseModel):
  id: int | None 
  user_id: int 
  total_items: int | None 
  total_amount: float | None 
  items: list[CartItemRead]
  is_active: bool 