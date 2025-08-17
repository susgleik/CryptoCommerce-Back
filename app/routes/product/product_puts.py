from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Product, Category, ProductCategory, Supplier
from ...schemas import product_schemas
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.put(
    "/{product_id}",
    response_model=product_schemas.ProductDetailResponse,
    description="Actualiza completamente un producto",
    tags=["Products"]
)
def update_product(
    product_id: int,
    product_update: product_schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Actualiza completamente un producto existente.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden actualizar productos.
    
    - **product_id**: ID del producto a actualizar
    - **product_update**: Datos del producto a actualizar (solo campos proporcionados)
    """
    
    # Verificar que el producto existe
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Verificar SKU único si se está actualizando
    if product_update.sku and product_update.sku != db_product.sku:
        existing_product = db.query(Product).filter(
            Product.sku == product_update.sku,
            Product.product_id != product_id
        ).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_update.sku}' already exists"
            )
    
    # Verificar que el proveedor existe si se está actualizando
    if product_update.supplier_id is not None:
        if product_update.supplier_id == 0:
            # Permitir establecer supplier_id como NULL enviando 0
            product_update.supplier_id = None
        else:
            supplier = db.query(Supplier).filter(
                Supplier.supplier_id == product_update.supplier_id
            ).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Supplier with ID {product_update.supplier_id} not found"
                )
    
    # Verificar que las categorías existen si se están actualizando
    if product_update.category_ids is not None:
        if product_update.category_ids:  # Si la lista no está vacía
            existing_categories = db.query(Category).filter(
                Category.category_id.in_(product_update.category_ids)
            ).all()
            
            existing_category_ids = {cat.category_id for cat in existing_categories}
            missing_category_ids = set(product_update.category_ids) - existing_category_ids
            
            if missing_category_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Categories with IDs {list(missing_category_ids)} not found"
                )
    
    try:
        # Actualizar campos del producto (excluyendo category_ids que se maneja por separado)
        update_data = product_update.dict(exclude_unset=True, exclude={'category_ids'})
        
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        # Actualizar categorías si se proporcionaron
        if product_update.category_ids is not None:
            # Eliminar todas las relaciones existentes
            db.query(ProductCategory).filter(
                ProductCategory.product_id == product_id
            ).delete()
            
            # Agregar nuevas relaciones
            for category_id in product_update.category_ids:
                product_category = ProductCategory(
                    product_id=product_id,
                    category_id=category_id
                )
                db.add(product_category)
        
        db.commit()
        db.refresh(db_product)
        
        # Cargar las relaciones para la respuesta
        product_with_relations = db.query(Product).options(
            joinedload(Product.supplier),
            joinedload(Product.categories)
        ).filter(Product.product_id == product_id).first()
        
        print(f"Product {product_id} updated by {current_user.user_type} {current_user.email}")
        
        return product_with_relations
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e.orig)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error updating product: {str(e)}"
        )


@router.patch(
    "/{product_id}",
    response_model=product_schemas.ProductDetailResponse,
    description="Actualiza parcialmente un producto",
    tags=["Products"]
)
def patch_product(
    product_id: int,
    product_update: product_schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Actualiza parcialmente un producto existente.
    
    Funciona igual que PUT pero semánticamente indica actualización parcial.
    Solo usuarios con rol ADMIN o STORE_STAFF pueden actualizar productos.
    
    - **product_id**: ID del producto a actualizar
    - **product_update**: Campos del producto a actualizar (solo los proporcionados)
    """
    return update_product(product_id, product_update, db, current_user)


@router.patch(
    "/{product_id}/toggle-status",
    response_model=product_schemas.ProductDetailResponse,
    description="Activa/desactiva un producto",
    tags=["Products"]
)
def toggle_product_status(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Alterna el estado activo/inactivo de un producto.
    
    - **product_id**: ID del producto
    """
    
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    try:
        # Alternar el estado
        old_status = db_product.is_active
        db_product.is_active = not db_product.is_active
        
        db.commit()
        db.refresh(db_product)
        
        # Cargar las relaciones para la respuesta
        product_with_relations = db.query(Product).options(
            joinedload(Product.supplier),
            joinedload(Product.categories)
        ).filter(Product.product_id == product_id).first()
        
        status_text = "activated" if db_product.is_active else "deactivated"
        print(f"Product {product_id} {status_text} (was {old_status}) by {current_user.user_type} {current_user.email}")
        
        return product_with_relations
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling product status: {str(e)}"
        )


@router.patch(
    "/{product_id}/stock",
    response_model=product_schemas.ProductDetailResponse,
    description="Actualiza el stock de un producto",
    tags=["Products"]
)
def update_product_stock(
    product_id: int,
    new_stock: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Actualiza únicamente el stock de un producto.
    
    - **product_id**: ID del producto
    - **new_stock**: Nuevo valor de stock (debe ser >= 0)
    """
    
    if new_stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot be negative"
        )
    
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    try:
        old_stock = db_product.online_stock
        db_product.online_stock = new_stock
        
        db.commit()
        db.refresh(db_product)
        
        # Cargar las relaciones para la respuesta
        product_with_relations = db.query(Product).options(
            joinedload(Product.supplier),
            joinedload(Product.categories)
        ).filter(Product.product_id == product_id).first()
        
        print(f"Product {product_id} stock updated from {old_stock} to {new_stock} by {current_user.user_type} {current_user.email}")
        
        return product_with_relations
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product stock: {str(e)}"
        )