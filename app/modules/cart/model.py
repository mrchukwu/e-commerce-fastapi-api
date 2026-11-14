from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

class Cart(Base):
  __tablename__ = "carts"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CartItem(Base):
  __tablename__ = "cart_items"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.id"), nullable=False)
  product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
  
  quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
