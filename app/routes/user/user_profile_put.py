from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...schemas.user_schemas import UserProfileUpdate, UserProfileResponse
from ...core.security import get_current_active_user

router = APIRouter()

@router.put(
    "/profile",
    response_model=UserProfileResponse,
    description="Actualiza completamente el perfil del usuario actual"
)
def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Actualiza completamente el perfil del usuario actual.

    Solo el usuario autenticado puede actualizar su propio perfil.
    PUT reemplaza todos los campos del perfil.

    - **first_name**: Nombre del usuario (opcional)
    - **last_name**: Apellido del usuario (opcional)
    - **address**: Dirección del usuario (opcional)
    - **phone**: Teléfono del usuario (opcional)
    - **profile_image**: URL de la imagen de perfil (opcional)
    """

    # Buscar el perfil del usuario
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first using POST /profile"
        )

    try:
        # Actualizar todos los campos (PUT reemplaza completamente)
        user_profile.first_name = profile_data.first_name
        user_profile.last_name = profile_data.last_name
        user_profile.address = profile_data.address
        user_profile.phone = profile_data.phone
        user_profile.profile_image = profile_data.profile_image

        db.commit()
        db.refresh(user_profile)

        print(f"Profile updated (PUT) for user {current_user.email} (ID: {current_user.user_id})")

        return user_profile

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )
