from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.common.price import calculate_selling_price
from app.modules.products.model import Product
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCreate, ProductRead, ProductUpdate
from math import ceil


class ProductService:

  def __init__(self, db: Session):
    self.product_repository = ProductRepository(db)
  
  def _serialize_product(self, product: Product) -> ProductRead:
    # convert sqlalchemy product model into pydantic model
    payload = ProductRead.model_validate(product)
  
    payload.selling_price = calculate_selling_price(payload.price, payload.discount_percent)

    return payload

  def list_products(
    self, 
    page: int, 
    limit: int,
    category_id: int | None = None,
    brand_name: str | None = None,
    is_active: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_price : str | None = None
  ) -> dict:
    products, total = self.product_repository.get_all(
      page, 
      limit, 
      category_id, 
      brand_name, 
      is_active, 
      min_price, 
      max_price, 
      sort_price
    )
    payload = [self._serialize_product(product) for product in products]
    return {
      "data":payload,
      "pagination": {
        "page": page,
        "limit": limit,
        "total": total, 
        "total_pages": ceil(total/limit) if limit > 0 else 0
      }
    }
  
  def get_product(self, product_id: int) -> ProductRead:
    product = self.product_repository.get_by_id(product_id)
    if not product:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

  def create_product(self, product: ProductCreate) -> ProductCreate:
    db_product = Product(**product.model_dump())
    saved_product = self.product_repository.create(db_product)
    return self._serialize_product(saved_product)

  def update_product(self, product_id, payload: ProductUpdate) -> ProductRead:
    product = self.product_repository.get_by_id(product_id)
    if not product:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in changes.items():
      setattr(product, field, value)
    
    updated_product = self.product_repository.update(product)
    return self._serialize_product(updated_product)
    
  def delete_product(self, product_id: int) -> None:
    product = self.product_repository.get_by_id(product_id)
    if product is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    self.product_repository.delete(product)
  
  def search_product(self, query: str) -> list[ProductRead]:
    products = self.product_repository.search(query)
    return [self._serialize_product(product) for product in products]
