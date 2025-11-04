from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...schemas.user_schemas import UserProfileCreate, UserProfileResponse
from ...core.security import get_current_active_user

router = APIRouter()

@router.post(
    "/profile",
    response_model=UserProfileResponse,
    description="Crea un perfil para el usuario actual",
    status_code=status.HTTP_201_CREATED
)
def create_user_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crea un perfil para el usuario actual.

    Solo el usuario autenticado puede crear su propio perfil.
    Si ya existe un perfil, retorna un error.

    - **first_name**: Nombre del usuario (opcional)
    - **last_name**: Apellido del usuario (opcional)
    - **address**: Dirección del usuario (opcional)
    - **phone**: Teléfono del usuario (opcional)
    - **profile_image**: URL de la imagen de perfil (opcional)
    """

    # Verificar si el usuario ya tiene un perfil
    existing_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has a profile. Use PUT or PATCH to update it."
        )

    try:
        # Crear el nuevo perfil
        new_profile = UserProfile(
            user_id=current_user.user_id,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            address=profile_data.address,
            phone=profile_data.phone,
            profile_image=profile_data.profile_image
        )

        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        print(f"Profile created for user {current_user.email} (ID: {current_user.user_id})")

        return new_profile

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating profile: {str(e)}"
        )
