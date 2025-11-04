from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database.database import get_db
from ...models.user_model import User, UserProfile
from ...core.security import get_current_active_user

router = APIRouter()

@router.delete(
    "/profile",
    description="Elimina el perfil del usuario actual",
    status_code=status.HTTP_200_OK
)
def delete_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Elimina el perfil del usuario actual.

    Solo el usuario autenticado puede eliminar su propio perfil.
    Esta acción no elimina la cuenta de usuario, solo el perfil adicional.

    Returns:
        Mensaje de confirmación con detalles del perfil eliminado
    """

    # Buscar el perfil del usuario
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id
    ).first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Nothing to delete."
        )

    try:
        # Guardar información antes de eliminar
        profile_info = {
            "profile_id": user_profile.profile_id,
            "first_name": user_profile.first_name,
            "last_name": user_profile.last_name
        }

        db.delete(user_profile)
        db.commit()

        print(f"Profile deleted for user {current_user.email} (ID: {current_user.user_id})")

        return {
            "message": "Profile successfully deleted",
            "deleted_profile": profile_info,
            "user_id": current_user.user_id,
            "user_email": current_user.email
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )
