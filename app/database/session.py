from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# elelctronic-ecommerce
database_url = settings.DATABASE_URL

engine = create_engine(url=database_url)

SessionLocal = sessionmaker(bind=engine)
