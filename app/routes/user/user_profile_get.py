from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...schemas.user_schemas import UserProfileResponse
from ...core.security import get_current_active_user

router = APIRouter()

@router.get(
    "/profile",
    response_model=UserProfileResponse,
    description="Obtiene el perfil del usuario actual",
)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene el perfil del usuario actual.

    Solo el usuario autenticado puede ver su propio perfil.

    Returns:
        Los datos del perfil del usuario
    """

    # Buscar el perfil del usuario
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one using POST /profile"
        )

    return user_profile
