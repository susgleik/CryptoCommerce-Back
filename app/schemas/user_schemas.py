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

# Schema para respuesta de usuario (sin password) - CORREGIDO CON ALIAS
class UserResponse(UserBase):
    id: int = Field(alias="user_id", description="ID único del usuario")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Permite usar tanto 'id' como 'user_id'
        allow_population_by_field_name = True  # Para retrocompatibilidad

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

# ADMIN SCHEMAS - CORREGIDOS CON ALIAS

class AdminUserInfo(BaseModel):
    id: int = Field(alias="user_id", description="ID único del usuario")
    username: str
    email: EmailStr
    user_type: str
    is_active: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True  # Permite usar tanto 'id' como 'user_id'
        allow_population_by_field_name = True  # Para retrocompatibilidad

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: AdminUserInfo
    permissions: List[str]

# Schema para verificar tokens admin
class TokenVerification(BaseModel):
    valid: bool
    user: AdminUserInfo
    permissions: List[str]

# Schemas adicionales para funciones admin
class UserRoleUpdate(BaseModel):
    user_type: str
    
    @validator('user_type')
    def validate_user_type(cls, v):
        allowed_types = ['common', 'store_staff', 'admin']
        if v not in allowed_types:
            raise ValueError(f'user_type debe ser uno de: {allowed_types}')
        return v

class UserStatusUpdate(BaseModel):
    is_active: bool

class StaffUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

# User Profile Schemas (si los necesitas)
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

# Schema completo para respuesta de usuario con perfil
class UserWithProfileResponse(UserResponse):
    profile: Optional[UserProfileResponse] = None
    
    class Config:
        from_attributes = True

# Schema para respuesta paginada
class PaginatedUserResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    items_per_page: int