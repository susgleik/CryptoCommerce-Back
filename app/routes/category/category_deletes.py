from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Category, Product, ProductCategory
from ...schemas import product_schemas
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.delete(
    "/{category_id}",
    response_model=dict,
    description="Desactiva una categoría (soft delete)",
    tags=["Categories"]
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Desactiva una categoría (soft delete) estableciendo is_active = False.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden eliminar categorías.
    No se permite eliminar categorías que tengan subcategorías activas.
    
    - **category_id**: ID de la categoría a desactivar
    
    Returns:
        Mensaje de confirmación con detalles de la categoría desactivada
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
    
    # Verificar si ya está desactivada
    if not db_category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category {category_id} is already inactive"
        )
    
    # Verificar si tiene subcategorías activas
    active_subcategories_count = db.query(Category).filter(
        Category.parent_category_id == category_id,
        Category.is_active == True
    ).count()
    
    if active_subcategories_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot deactivate category: has {active_subcategories_count} active subcategories. Please deactivate them first."
        )
    
    # Contar productos asociados
    products_count = db.query(Product).filter(
        Product.categories.any(Category.category_id == category_id),
        Product.is_active == True
    ).count()
    
    try:
        # Soft delete - solo desactivar
        db_category.is_active = False
        db.commit()
        db.refresh(db_category)
        
        print(f"Category {category_id} ({db_category.name}) deactivated by {current_user.user_type} {current_user.email}")
        
        return {
            "message": "Category successfully deactivated",
            "category_id": category_id,
            "category_name": db_category.name,
            "is_active": False,
            "affected_active_products": products_count,
            "note": "Products associated with this category are still active. Category can be restored using the restore endpoint.",
            "action_performed_by": {
                "user_type": current_user.user_type,
                "email": current_user.email
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating category: {str(e)}"
        )


@router.delete(
    "/{category_id}/hard",
    response_model=dict,
    description="Elimina permanentemente una categoría (hard delete)",
    tags=["Categories"]
)
def hard_delete_category(
    category_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Elimina permanentemente una categoría de la base de datos (hard delete).
    
    ⚠️ ADVERTENCIA: Esta operación es IRREVERSIBLE.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden eliminar categorías permanentemente.
    Por seguridad, solo se permite eliminar categorías que:
    - No tengan subcategorías
    - No tengan productos asociados (a menos que force=True)
    
    - **category_id**: ID de la categoría a eliminar
    - **force**: Si es True, elimina la categoría incluso si tiene productos asociados
    
    Returns:
        Mensaje de confirmación de eliminación permanente
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
    
    # Verificar si tiene subcategorías (no se permite eliminar con subcategorías)
    subcategories_count = db.query(Category).filter(
        Category.parent_category_id == category_id
    ).count()
    
    if subcategories_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category: has {subcategories_count} subcategories. Please delete or move them first."
        )
    
    # Contar productos asociados
    products_count = db.query(ProductCategory).filter(
        ProductCategory.category_id == category_id
    ).count()
    
    if products_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category: has {products_count} associated products. Use force=True to delete anyway or remove products from this category first."
        )
    
    category_name = db_category.name
    
    try:
        # Eliminar relaciones con productos primero (se hará automáticamente con CASCADE)
        # pero lo hacemos explícito para mayor claridad
        if products_count > 0:
            db.query(ProductCategory).filter(
                ProductCategory.category_id == category_id
            ).delete(synchronize_session=False)
        
        # Hard delete - eliminar permanentemente
        db.delete(db_category)
        db.commit()
        
        print(f"Category {category_id} ({category_name}) permanently deleted by {current_user.user_type} {current_user.email}")
        
        return {
            "message": "Category permanently deleted",
            "category_id": category_id,
            "category_name": category_name,
            "products_unlinked": products_count,
            "warning": "This action is IRREVERSIBLE. The category cannot be restored.",
            "action_performed_by": {
                "user_type": current_user.user_type,
                "email": current_user.email
            }
        }
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category due to database constraints: {str(e.orig)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )


@router.delete(
    "/bulk/deactivate",
    response_model=dict,
    description="Desactiva múltiples categorías en una sola operación",
    tags=["Categories"]
)
def bulk_deactivate_categories(
    category_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Desactiva múltiples categorías en una sola operación.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden desactivar categorías.
    
    - **category_ids**: Lista de IDs de categorías a desactivar
    
    Returns:
        Resumen de la operación con categorías desactivadas y errores
    """
    
    if not category_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category IDs list cannot be empty"
        )
    
    if len(category_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate more than 100 categories at once"
        )
    
    deactivated = []
    errors = []
    
    for category_id in category_ids:
        try:
            # Verificar que existe
            db_category = db.query(Category).filter(
                Category.category_id == category_id
            ).first()
            
            if not db_category:
                errors.append({
                    "category_id": category_id,
                    "error": "Category not found"
                })
                continue
            
            # Verificar si ya está inactiva
            if not db_category.is_active:
                errors.append({
                    "category_id": category_id,
                    "error": "Category is already inactive"
                })
                continue
            
            # Verificar subcategorías activas
            active_subcategories = db.query(Category).filter(
                Category.parent_category_id == category_id,
                Category.is_active == True
            ).count()
            
            if active_subcategories > 0:
                errors.append({
                    "category_id": category_id,
                    "error": f"Has {active_subcategories} active subcategories"
                })
                continue
            
            # Desactivar
            db_category.is_active = False
            deactivated.append({
                "category_id": category_id,
                "category_name": db_category.name
            })
            
        except Exception as e:
            errors.append({
                "category_id": category_id,
                "error": str(e)
            })
    
    try:
        db.commit()
        
        print(f"Bulk deactivation: {len(deactivated)} categories by {current_user.user_type} {current_user.email}")
        
        return {
            "message": "Bulk deactivation completed",
            "total_requested": len(category_ids),
            "successfully_deactivated": len(deactivated),
            "failed": len(errors),
            "deactivated_categories": deactivated,
            "errors": errors,
            "action_performed_by": {
                "user_type": current_user.user_type,
                "email": current_user.email
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during bulk deactivation: {str(e)}"
        )