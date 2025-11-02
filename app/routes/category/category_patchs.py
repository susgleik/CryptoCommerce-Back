from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Category
from ...schemas import product_schemas
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.patch(
    "/{category_id}",
    response_model=product_schemas.CategoryResponse,
    description="Actualiza parcialmente una categoría",
    tags=["Categories"]
)
def update_category_partial(
    category_id: int,
    category_update: product_schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Actualiza parcialmente los campos de una categoría existente.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden actualizar categorías.
    Solo se actualizan los campos que se envían en la petición.
    
    - **category_id**: ID de la categoría a actualizar
    - **name**: Nuevo nombre (opcional)
    - **description**: Nueva descripción (opcional)
    - **category_image**: Nueva URL de imagen (opcional)
    - **parent_category_id**: Nuevo ID de categoría padre (opcional)
    - **is_active**: Nuevo estado activo/inactivo (opcional)
    """
    
    # Verificar que la categoría existe
    db_category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    # Obtener solo los campos que fueron enviados (exclude_unset=True)
    update_data = category_update.dict(exclude_unset=True)
    
    # Validar nombre único si se está actualizando
    if "name" in update_data and update_data["name"] != db_category.name:
        existing_category = db.query(Category).filter(
            Category.name.ilike(update_data["name"]),
            Category.category_id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{update_data['name']}' already exists"
            )
    
    # Validar categoría padre si se está actualizando
    if "parent_category_id" in update_data and update_data["parent_category_id"] is not None:
        # No permitir que una categoría sea su propio padre
        if update_data["parent_category_id"] == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category cannot be its own parent"
            )
        
        # Verificar que la categoría padre existe
        parent_category = db.query(Category).filter(
            Category.category_id == update_data["parent_category_id"]
        ).first()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID {update_data['parent_category_id']} not found"
            )
        
        # Verificar que la categoría padre está activa
        if not parent_category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category with ID {update_data['parent_category_id']} is not active"
            )
        
        # Verificar que no crearía una referencia circular
        def check_circular_reference(parent_id, original_id):
            parent = db.query(Category).filter(Category.category_id == parent_id).first()
            if not parent:
                return False
            if parent.parent_category_id == original_id:
                return True
            if parent.parent_category_id:
                return check_circular_reference(parent.parent_category_id, original_id)
            return False
        
        if check_circular_reference(update_data["parent_category_id"], category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set parent category: would create circular reference"
            )
    
    # Validar desactivación de categoría con subcategorías activas
    if "is_active" in update_data and not update_data["is_active"]:
        active_subcategories = db.query(Category).filter(
            Category.parent_category_id == category_id,
            Category.is_active == True
        ).count()
        
        if active_subcategories > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate category: has {active_subcategories} active subcategories"
            )
    
    try:
        # Actualizar los campos
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        
        print(f"Category {category_id} updated by {current_user.user_type} {current_user.email}")
        
        return db_category
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating category: {str(e.orig)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating category: {str(e)}"
        )


@router.patch(
    "/{category_id}/toggle-status",
    response_model=dict,
    description="Cambia el estado activo/inactivo de una categoría",
    tags=["Categories"]
)
def toggle_category_status(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Cambia el estado activo/inactivo de una categoría.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden cambiar el estado.
    
    - **category_id**: ID de la categoría
    
    Returns:
        Mensaje con el nuevo estado de la categoría
    """
    
    db_category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    new_status = not db_category.is_active
    
    # Si se va a activar, verificar que el padre esté activo
    if new_status and db_category.parent_category_id:
        parent = db.query(Category).filter(
            Category.category_id == db_category.parent_category_id
        ).first()
        
        if parent and not parent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot activate: parent category (ID: {parent.category_id}) is inactive"
            )
    
    # Si se va a desactivar, verificar subcategorías activas
    if not new_status:
        active_subcategories = db.query(Category).filter(
            Category.parent_category_id == category_id,
            Category.is_active == True
        ).count()
        
        if active_subcategories > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate: has {active_subcategories} active subcategories"
            )
    
    try:
        db_category.is_active = new_status
        db.commit()
        db.refresh(db_category)
        
        action = "activated" if new_status else "deactivated"
        print(f"Category {category_id} {action} by {current_user.user_type} {current_user.email}")
        
        return {
            "message": f"Category successfully {action}",
            "category_id": category_id,
            "category_name": db_category.name,
            "is_active": new_status,
            "action_performed_by": {
                "user_type": current_user.user_type,
                "email": current_user.email
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling category status: {str(e)}"
        )   