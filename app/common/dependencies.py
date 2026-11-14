from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import SessionLocal
from app.modules.users.model import User
from app.modules.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def get_current_user(
  token: str = Depends(oauth2_scheme),
  db: Session = Depends(get_db)
):
  payload = decode_access_token(token)
  subject = payload.get("sub")

  if subject is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail = "Invalid token..."
    )
  
  user_id = int(subject)
  user_repository = UserRepository(db)
  user = user_repository.get_by_id(user_id)

  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail = "user not found"
    )
  if not user.is_active:

    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Inactivate account",
    )
  
  return user