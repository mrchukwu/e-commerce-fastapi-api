
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
  name: str
  parent_id: int | None = None
  

class CategoryCreate(CategoryBase):
  pass

class CategoryUpdate(CategoryBase):
  name: str | None = None
  parent_id: int | None = None
  
class CategoryRead(CategoryBase):
  id: int

  class Config: 
    from_attributes = True