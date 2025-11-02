from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Category
from ...schemas import product_schemas
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.put(
    "/{category_id}",
    response_model=product_schemas.CategoryResponse,
    description="Actualiza completamente una categoría",
    tags=["Categories"]
)
def update_category_full(
    category_id: int,
    category_update: product_schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Actualiza completamente una categoría existente (PUT - reemplazo total).
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden actualizar categorías.
    Todos los campos deben ser proporcionados.
    
    - **category_id**: ID de la categoría a actualizar
    - **name**: Nombre de la categoría (requerido)
    - **description**: Descripción de la categoría (opcional)
    - **category_image**: URL de la imagen de la categoría (opcional)
    - **parent_category_id**: ID de la categoría padre (opcional)
    - **is_active**: Estado activo/inactivo (requerido)
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
    
    # Validar nombre único si cambió
    if category_update.name != db_category.name:
        existing_category = db.query(Category).filter(
            Category.name.ilike(category_update.name),
            Category.category_id != category_id
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_update.name}' already exists"
            )
    
    # Validar categoría padre si se especifica
    if category_update.parent_category_id is not None:
        # No permitir que una categoría sea su propio padre
        if category_update.parent_category_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category cannot be its own parent"
            )
        
        # Verificar que la categoría padre existe
        parent_category = db.query(Category).filter(
            Category.category_id == category_update.parent_category_id
        ).first()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID {category_update.parent_category_id} not found"
            )
        
        # Verificar que la categoría padre está activa
        if not parent_category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category with ID {category_update.parent_category_id} is not active"
            )
        
        # Verificar que no crearía una referencia circular
        def check_circular_reference(parent_id, original_id):
            """Verifica referencias circulares en la jerarquía"""
            parent = db.query(Category).filter(Category.category_id == parent_id).first()
            if not parent:
                return False
            if parent.parent_category_id == original_id:
                return True
            if parent.parent_category_id:
                return check_circular_reference(parent.parent_category_id, original_id)
            return False
        
        if check_circular_reference(category_update.parent_category_id, category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot set parent category: would create circular reference"
            )
    
    # Validar desactivación si tiene subcategorías activas
    if not category_update.is_active:
        active_subcategories = db.query(Category).filter(
            Category.parent_category_id == category_id,
            Category.is_active == True
        ).count()
        
        if active_subcategories > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate category: has {active_subcategories} active subcategories. Please deactivate them first."
            )
    
    try:
        # Actualizar todos los campos
        db_category.name = category_update.name
        db_category.description = category_update.description
        db_category.category_image = category_update.category_image
        db_category.parent_category_id = category_update.parent_category_id
        db_category.is_active = category_update.is_active
        
        db.commit()
        db.refresh(db_category)
        
        print(f"Category {category_id} fully updated by {current_user.user_type} {current_user.email}")
        
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


@router.put(
    "/{category_id}/move",
    response_model=product_schemas.CategoryResponse,
    description="Mueve una categoría a una nueva categoría padre",
    tags=["Categories"]
)
def move_category(
    category_id: int,
    new_parent_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Mueve una categoría a una nueva categoría padre o la convierte en categoría raíz.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden mover categorías.
    
    - **category_id**: ID de la categoría a mover
    - **new_parent_id**: ID de la nueva categoría padre (None para hacerla categoría raíz)
    
    Returns:
        La categoría actualizada con su nueva ubicación
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
    
    # Si se especifica un nuevo padre
    if new_parent_id is not None:
        # No permitir que una categoría sea su propio padre
        if new_parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category cannot be its own parent"
            )
        
        # Verificar que el nuevo padre existe y está activo
        new_parent = db.query(Category).filter(
            Category.category_id == new_parent_id
        ).first()
        
        if not new_parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID {new_parent_id} not found"
            )
        
        if not new_parent.is_active and db_category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot move active category to inactive parent (ID: {new_parent_id})"
            )
        
        # Verificar referencias circulares
        def check_circular_reference(parent_id, original_id):
            parent = db.query(Category).filter(Category.category_id == parent_id).first()
            if not parent:
                return False
            if parent.parent_category_id == original_id:
                return True
            if parent.parent_category_id:
                return check_circular_reference(parent.parent_category_id, original_id)
            return False
        
        if check_circular_reference(new_parent_id, category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move category: would create circular reference"
            )
    
    try:
        old_parent_id = db_category.parent_category_id
        db_category.parent_category_id = new_parent_id
        
        db.commit()
        db.refresh(db_category)
        
        move_type = "root level" if new_parent_id is None else f"under category {new_parent_id}"
        print(f"Category {category_id} moved from {old_parent_id} to {move_type} by {current_user.user_type} {current_user.email}")
        
        return db_category
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error moving category: {str(e)}"
        )