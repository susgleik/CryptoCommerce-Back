from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Security
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Any
from ...database.database import get_db
from ...models.product_model import Product, Category
from ...schemas import product_schemas
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ...auth.dependencies import get_current_user, get_current_admin, validate_token_and_get_user
from ...models.product_model import ProductCategory 

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/",
    response_model=product_schemas.ProductResponse,
    description="se crea un nuevo producto",
    tags=["Products"]
)
def create_product(
    product: product_schemas.ProductCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
): 
    current_user = validate_token_and_get_user(credentials, db)
    
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
        
    existing_product = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with this SKU '{product.sku}' already exists"
        ) 
        
    if product.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.supplier == product.supplier_id).first()
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
        
        if len(existing_categories) != len(product.category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more category IDs are invalid"
            )
            
    try:
        db_product = Product(
            name=product.name,
            price=product.prince,  # Nota: hay un typo en el schema (prince vs price)
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
