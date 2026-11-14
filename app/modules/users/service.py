from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserRead, UserRole, UserUpdate


class UserService:
  def __init__(self, db: Session) -> None:
    self.user_repository = UserRepository(db)

  def _dump_user(self, user: User) -> dict:
    return UserRead.model_validate(user).model_dump()
  
  def list_users(self) -> list[dict]:
    users = self.user_repository.get_all_users()
    result = [self._dump_user(user) for user in users]
    return result
  
  def get_user(self, user_id:int) -> UserRead:
    user = self.user_repository.get_by_id(user_id)

    if user is None:
      raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )
    return self._dump_user(user)

  def get_current_user(self, user: User) -> UserRead:
    return self._dump_user(user)
  
  def update_user(self, user: User, paylaod: UserUpdate):
    user = self.user_repository.get_by_id(user)

    if user is None:
      raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )

    changes= paylaod.model_dump(exclude_unset=True)

    if "full_name" in changes:
      user.full_name = changes["full_name"]

    db_user = self.user_repository.update(user)

    return self._dump_user(db_user)

  def delete_user(self, user_id: int) -> None:
    user = self.user_repository.get_by_id(user_id)

    if user is None:
      raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )

    self.user_repository.delete(user)
    return {"message":"User deleted successfully"}

  def ensure_admin_user(self) -> None:
    admin_email = "kennedy@gmail.com"
    admin_password = "ken123456"
    existing_admin = self.user_repository.get_by_email(admin_email)

    if existing_admin is not None:
      return

    admin_user = User(
      full_name = "kennedy Chukwu",
      email = admin_email,
      password_hash = hash_password(admin_password),
      is_active = True,
      role = UserRole.ADMIN.value
    )
    self.user_repository.create(admin_user)