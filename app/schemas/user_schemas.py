from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal
from datetime import datetime

# Usar Literal en lugar de Enum para mayor compatibilidad
UserTypeEnum = Literal["common", "admin", "store_staff"]

# Base schema para validar datos comunes
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, description="Nombre de usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    is_active: Optional[bool] = True
    user_type: UserTypeEnum = "common"

# Schema para crear un usuario (request)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

# Schema para login
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

# Schema para actualizar un usuario (opcional todos los campos)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    is_active: Optional[bool] = None
    user_type: Optional[UserTypeEnum] = None

# Schema para respuesta de usuario (sin password)
class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        orm_mode = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    user_type: Optional[str] = None
    exp: Optional[datetime] = None

# User Profile Schemas
class UserProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    profile_id: int
    user_id: int
    
    class Config:
        from_attributes = True
        orm_mode = True

# Schema completo para respuesta de usuario con perfil
class UserWithProfileResponse(UserResponse):
    profile: Optional[UserProfileResponse] = None
    
    class Config:
        from_attributes = True
        orm_mode = True

# Schema para respuesta paginada
class PaginatedUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    items_per_page: int