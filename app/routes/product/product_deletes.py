from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Product, ProductCategory
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.delete(
    "/{product_id}",    
    status_code=status.HTTP_204_NO_CONTENT,
    description="Elimina un producto permanentemente",
    tags=["Products"]
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Elimina permanentemente un producto de la base de datos.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden eliminar productos.
    
    **ADVERTENCIA**: Esta acción es irreversible. El producto y todas sus 
    relaciones serán eliminados permanentemente.
    
    - **product_id**: ID del producto a eliminar
    
    Returns:
        HTTP 204 No Content si la eliminación fue exitosa
    """
    
    print(f"=== DELETE PRODUCT DEBUG ===")
    print(f"Product ID: {product_id}")
    print(f"User: {current_user.email}")
    print(f"User Type: {current_user.user_type}")
    print(f"User Type Type: {type(current_user.user_type)}")
    
    # check if product exists
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    print(f"Product found: {db_product.name} (ID: {db_product.product_id})")
    
    try:
        # save info for log before deletion
        product_name = db_product.name
        product_sku = db_product.sku
        
        # delete product (the related ProductCategory entries will be deleted automatically cascade)
        db.delete(db_product)
        db.commit()
        
        print(f"Product {product_id} ({product_name}, SKU: {product_sku}) deleted by user {current_user.username}")
        
        
        return None
    
    except IntegrityError as e:
        db.rollback()
        # this could happe if the product is referenced in other tables
        # if dont have cascade delete set up
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete product. It may be referenced by other records: {str(e.orig)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting product: {str(e)}"
        )
        
@router.delete(
    "/{product_id}/soft",
    response_model=dict,
    description="Desactiva un producto (eliminación suave)",
    tags=["Products"]
)
def soft_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Desactiva un producto en lugar de eliminarlo permanentemente (soft delete).
    
    Esta es una alternativa más segura a la eliminación permanente.
    El producto se marca como inactivo pero se mantiene en la base de datos.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden desactivar productos.
    
    - **product_id**: ID del producto a desactivar
    
    Returns:
        Mensaje de confirmación con detalles del producto desactivado
    """
    
    # Verificar que el producto existe
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Verificar si ya está inactivo
    if not db_product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {product_id} is already inactive"
        )
    
    try:
        # Desactivar el producto
        db_product.is_active = False
        db.commit()
        db.refresh(db_product)
        
        print(f"Product {product_id} ({db_product.name}) soft deleted by {current_user.user_type} {current_user.email}")
        
        return {
            "message": "Product successfully deactivated",
            "product_id": product_id,
            "product_name": db_product.name,
            "product_sku": db_product.sku,
            "is_active": db_product.is_active,
            "action_performed_by": {
                "user_type": current_user.user_type,
                "email": current_user.email
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating product: {str(e)}"
        )