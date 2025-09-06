# app/core/jwt_handler.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi.security import HTTPBearer

# Configuración
SECRET_KEY = "tu_clave_secreta_muy_segura"  # Cambia esto en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, is_admin: bool = False) -> str:
    """
    Crear token de acceso con información del rol
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow(timezone.utc) + expires_delta
    else:
        minutes = ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES if is_admin else ACCESS_TOKEN_EXPIRE_MINUTES
        expire = datetime.utcnow(timezone.utc) + timedelta(minutes=minutes)
    
    to_encode.update({
        "exp": expire, 
        "iat": datetime.now(timezone.utc),
        "token_type": "admin" if is_admin else "user"
        })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_admin_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear token específico para administradores
    """
    return create_access_token(data, expires_delta, is_admin=True)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def verify_admin_token(token: str) -> dict:
    """
    Verificar que el token es de tipo admin
    """
    payload = verify_token(token)
    if not payload:
        return None
    
    # Verificar que es un token admin
    if payload.get("token_type") != "admin":
        return None
    
    return payload

def get_password_hash(password: str) -> str:
    """
    Genera un hash de la contraseña usando bcrypt
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash
    """
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )