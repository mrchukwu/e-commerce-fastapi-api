
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead, UserRole


class AuthService:
  def __init__(self, db: Session):
    self.user_repository = UserRepository(db)
  
  def _dump_user(self, user: User) -> dict:
    return UserRead.model_validate(user).model_dump()
  
  def regsiter(self, payload: RegisterRequest) -> dict:
    exisiting_user = self.user_repository.get_by_email(payload.email)

    if exisiting_user is not None:
      raise HTTPException(
        status_code= status.HTTP_409_CONFLICT, 
        detail="User with this email already exists."
      )

    user = User(
      full_name = payload.full_name,
      email = payload.email,
      password_hash = hash_password(payload.password),
      is_active = True,
      role = UserRole.CUSTOMER.value
    )

    db_user = self.user_repository.create(user)
    created_user = self._dump_user(db_user)

    # create access token
    access_token = create_access_token(
      str(db_user.id),
      db_user.role
    )

    return {
      "message": "User registered successfully",
      "access_token": access_token,
      "user": created_user
    }

  # login
  def login(self, payload: LoginRequest) -> dict:
    user = self.user_repository.get_by_email(payload.email)
    
    if user is None or not user.is_active:
      raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid email or password"
      )
    
    if not verify_password(payload.password, user.password_hash):
      raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid email or password"
      )
    
    access_token = create_access_token(str(user.id), user.role)

    pydantic_user = self._dump_user(user)

    return {
      "message": "Login successful",
      "access_token": access_token,
      "token_type": "bearer",
      "user": pydantic_user
    }
    
