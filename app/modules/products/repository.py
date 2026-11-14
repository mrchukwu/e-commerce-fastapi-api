from operator import or_

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.products.model import Product

# 1 page first_10, 2 page next_10, 3 page next_10
# ofset => 0, 10, 20

# 10 limit
# (1 - 1) * 10 => 0
# (2 -1) * 10 => 10
# (3 -1) * 10 => 20

class ProductRepository:

  def __init__(self, db: Session) -> None:
    self.db = db
  
  def get_all(
    self, 
    page: int, 
    limit: int, 
    category_id: int | None = None,
    brand_name: str | None = None,
    is_active: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_price : str | None = None
    ) -> tuple[list[Product], int]:

    statement = select(Product)

    count_statement = select(func.count()).select_from(Product)

    if category_id is not None:
      statement=statement.where(
        Product.category_id == category_id
      )
      count_statement = count_statement.where(
        Product.category_id == category_id
      )
    
    if brand_name is not None:
      brand_contions = func.lower(Product.brand_name) == brand_name.lower( )
      statement = statement.where(brand_contions)
      count_statement = count_statement.where(brand_contions)
    
    if is_active is not None:
      statement = statement.where(Product.is_active == is_active)
      count_statement = count_statement.where(Product.is_active == is_active)

    if min_price is not None:
      statement = statement.where(Product.price >= min_price)
      count_statement = count_statement.where(Product.price >= min_price)

    if max_price is not None:
      statement = statement.where(Product.price <= max_price)
      count_statement = count_statement.where(Product.price <= max_price)

    total = self.db.scalar(count_statement) or 0    

    #sorting product
    if sort_price == "asc":
      statement = statement.order_by(Product.price.asc())
    elif sort_price == "desc":
      statement = statement.order_by(Product.price.desc())
    else:
      statement = statement.order_by(Product.id.desc())

    offset = (page-1) * limit
    
    products = self.db.scalars(statement.offset(offset).limit(limit)).all()
    return products, total
  
  def get_by_id(self, product_id: int) -> Product | None:
    return self.db.get(Product, product_id)
  
  def create(self, product: Product) -> Product:
    self.db.add(product)
    self.db.commit()
    self.db.refresh(product)
    return product
  
  def update(self, product: Product) -> Product:
    self.db.add(product)   
    self.db.commit()
    self.db.refresh(product)
    return product
  
  def delete(self, product: Product) -> None:
    self.db.delete(product)
    self.db.commit()
  
  # example: Samsunjg s24 ultra 500gb, 12 am
  # search : s24 ultra => samsung, s24, ultra, 500gb, 12gb ram
  # search : samsung => samsung
  # search : 500gb => 500gb
  # search : 12gb => 12gb

  def search(self, query: str) -> list[Product]:
    search_term = f"%{query.lower()}%"

    statement = (
      select(Product).where(
        or_(
          Product.name.ilike(search_term),
          Product.brand_name.ilike(search_term),
          # Product.description.ilike(search_term)
        )
      ).order_by(Product.id.asc())
    )
    return self.db.scalars(statement).all()