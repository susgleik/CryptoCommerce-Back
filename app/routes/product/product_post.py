from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Security
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ...database.database import get_db
from ...models.product_model import Product, Category
from ...schemas import product_schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.product_model import ProductCategory 
from ...models.user_model import User

router = APIRouter()

@router.post(
    "/",
    response_model=product_schemas.ProductDetailResponse,
    description="se crea un nuevo producto",
    tags=["Products"]
)
def create_product(
    product: product_schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user),
): 
    """
    Crea un nuevo producto.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden crear productos.
    
    - **name**: Nombre del producto
    - **price**: Precio del producto
    - **sku**: SKU único del producto
    - **description**: Descripción del producto
    - **online_stock**: Stock disponible
    - **supplier_id**: ID del proveedor (opcional)
    - **category_ids**: Lista de IDs de categorías
    """
        
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with this SKU '{product.sku}' already exists"
        ) 
        
    if product.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == product.supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier with ID {product.supplier_id} not found"
            )
    
    # Verificar que las categorías existen
    if product.category_ids:
        existing_categories = db.query(Category).filter(
            Category.category_id.in_(product.category_ids)
        ).all()
        
        existing_category_ids = {cat.category_id for cat in existing_categories}
        missing_category_ids = set(product.category_ids) - existing_category_ids
        
        if missing_category_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categories with IDs {list(missing_category_ids)} not found"
            )
            
    try:
        db_product = Product(
            name=product.name,
            price=product.price,  # Nota: hay un typo en el schema (prince vs price)
            description=product.description,
            online_stock=product.online_stock,
            sku=product.sku,
            release_date=product.release_date,
            is_featured=product.is_featured,
            is_active=product.is_active,
            product_type=product.product_type,
            attributes=product.attributes,
            product_image=product.product_image,
            supplier_id=product.supplier_id
        )
        
        db.add(db_product)
        db.flush()
        
        if product.category_ids:
            for category_id in product.category_ids:
                product_category = ProductCategory(
                    product_id=db_product.product_id,
                    category_id=category_id
                )
                db.add(product_category)
        db.commit()
        db.refresh(db_product)
        
        # Cargar las relaciones para la respuesta
        product_with_relations = db.query(Product).options(
            joinedload(Product.supplier),
            joinedload(Product.categories)
        ).filter(Product.product_id == db_product.product_id).first()
        
        print(f"Product created by admin {current_user.email}: {db_product.name}")
        
        return product_with_relations
        
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {str(e.orig)}"
        )    
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )


@router.post(
    "/{product_id}/restore",
    response_model=dict,
    description="Reactiva un producto desactivado",
    tags=["Products"]
)
def restore_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user)
):
    """
    Reactiva un producto que fue desactivado anteriormente.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden reactivar productos.
    
    - **product_id**: ID del producto a reactivar
    
    Returns:
        Mensaje de confirmación con detalles del producto reactivado
    """
    
    # Verificar que el producto existe
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Verificar si ya está activo
    if db_product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {product_id} is already active"
        )
    
    try:
        # Reactivar el producto
        db_product.is_active = True
        db.commit()
        db.refresh(db_product)
        
        print(f"Product {product_id} ({db_product.name}) restored by {current_user.user_type} {current_user.email}")
        
        return {
            "message": "Product successfully reactivated",
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
            detail=f"Error reactivating product: {str(e)}"
        )