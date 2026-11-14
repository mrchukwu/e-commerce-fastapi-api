from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserRead


class RegisterRequest(BaseModel):
  full_name: str = Field(..., min_length=3, max_length=150, description="Full name of the user")
  email: EmailStr 
  password: str = Field(..., min_length=8, max_length=255, description="Password must be at least 8 characters")

class RegisterResponse(BaseModel):
  full_name: str
  email: str

class LoginRequest(BaseModel):
  email: EmailStr 
  password: str 

class LoginResponse(BaseModel):
  access_token: str
  token_type: str
  user: UserRead