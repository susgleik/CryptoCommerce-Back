# schemas/user_schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    user_type: str = Field("common", description="Tipo de usuario (common o admin)")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

class UserResponse(UserBase):
    user_id: int
    user_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class PaginatedUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    items_per_page: int