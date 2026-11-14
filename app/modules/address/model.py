from fastapi import HTTPException
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Address(Base):
    __tablename__ = "addresses"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address_line1 : Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2 : Mapped[str] = mapped_column(String(255), nullable=True)
    city : Mapped[str] = mapped_column(String(100), nullable=False)
    state : Mapped[str] = mapped_column(String(100), nullable=False)
    country : Mapped[str] = mapped_column(String(100), nullable=False, default="Nigeria")
    postal_code : Mapped[str] = mapped_column(String(20), nullable=False, default="101001")
    is_default : Mapped[bool] = mapped_column(Boolean, default=False)