from pydantic import BaseModel, ConfigDict, Field


class SpecificationItem(BaseModel):
  name: str
  value: str

class Specidication(BaseModel):
  section: str
  features: list[SpecificationItem]

class ProductBase(BaseModel):
  name: str
  brand_name: str
  model_no: str
  description: str
  warrenty: str
  discount_percent : float = Field(..., ge=0, le=100)
  stock_quantity: int = Field(..., ge=0)
  is_active : bool = Field(default=True)
  price: float = Field(..., ge=0)
  image_url: str
  category_id: int
  additional_images: list[str] = Field(default_factory=list)
  highlights: list[str] = Field(default_factory=list)
  specification: list[Specidication] = Field(default_factory=list)


class ProductCreate(ProductBase):
  pass

class ProductUpdate(ProductBase):
  pass

class ProductResponse(ProductBase):
  id: int
  selling_price: float

  model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str | None = None
    brand_name: str | None = None
    model_no: str | None = None
    description: str | None = None
    warrenty: str | None = None
    discount_percent: float | None = Field(default=None, ge=0, le=100)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = Field(default=None)
    price: float | None = Field(default=None, ge=0)
    image_url: str | None = None
    category_id: int | None = None
    addtional_images: list[str] | None = Field(default=None)
    highlights: list[str] | None = Field(default=None)
    specification: list[Specidication] | None = Field(default=None)

class ProductRead(ProductBase):
  id: int
  selling_price: float | None = None

  class Config: 
    from_attributes = True