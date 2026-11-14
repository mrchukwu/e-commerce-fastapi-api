from fastapi import FastAPI

from app.api.router import api_router
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.modules.users.service import UserService

app = FastAPI(
  title = "Electronics Ecommerce Project",
  description = "API for managing ecommerce website",
  version = "1.0.0"
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()
UserService(db).ensure_admin_user()


@app.get("/")
def home():
  return {"message": "Welcome to the FastAPI E-Commerce API"}


app.include_router(api_router, prefix="/api/v1")