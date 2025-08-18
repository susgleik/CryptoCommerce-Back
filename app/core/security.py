from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..database.database import get_db
from ..models.user_model import User

# USAR DIRECTAMENTE LOS VALORES EN LUGAR DE SETTINGS
SECRET_KEY = "tu_clave_secreta_muy_segura"  # LA MISMA QUE EN jwt_handler.py
ALGORITHM = "HS256"

# Inicializar HTTPBearer UNA SOLA VEZ
security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Función base para obtener el usuario actual desde el token.
    """
    
    print(f"=== SECURITY DEBUG ===")
    print(f"Credentials received: {credentials is not None}")
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        print(f"Token received: {token[:20]}...")
        print(f"Using SECRET_KEY: {SECRET_KEY[:10]}...")
        print(f"Using ALGORITHM: {ALGORITHM}")
        
        # USAR LA MISMA SECRET_KEY QUE EN jwt_handler.py
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload decoded successfully: {payload}")
        
        email: str = payload.get("sub")
        print(f"Email from token: {email}")
        
        if email is None:
            print("Email is None in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuario en la base de datos
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"User not found in database: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    print(f"User found: {user.email}, type: {user.user_type}")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica que el usuario esté activo.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user