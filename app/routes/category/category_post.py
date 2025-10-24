from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ...database.database import get_db
from ...models.product_model import Category
from ...schemas import product_schemas
from ...core.dependencies import get_current_admin_or_staff_user
from ...models.user_model import User

router = APIRouter()

@router.post(
    "/",
    response_model=product_schemas.CategoryResponse,
    description="Crea una nueva categoría",
    tags=["Categories"]
)
def create_category(
    category: product_schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_staff_user),
):
    
    """
    Crea una nueva categoría.
    
    Solo usuarios con rol ADMIN o STORE_STAFF pueden crear categorías.
    
    - **name**: Nombre de la categoría (requerido)
    - **description**: Descripción de la categoría (opcional)
    - **category_image**: URL de la imagen de la categoría (opcional)
    - **parent_category_id**: ID de la categoría padre para subcategorías (opcional)
    - **is_active**: Estado activo/inactivo (default: True)
    
    """
    
    existing_category = db.query(Category).filter(Category.name.ilike(category.name)).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists"
        )
    
    parent_id = category.parent_category_id
    if parent_id is not None and parent_id == 0:
        parent_id = None

    if parent_id is not None:
        parent_category = db.query(Category).filter(
            Category.category_id == category.parent_category_id
        ).first()
        
        if not parent_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID {category.parent_category_id} not found"
            )
            
        if not parent_category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category with ID {category.parent_category_id} is not active"
            )
        
    try:
        db_category = Category(
            name=category.name,
            description=category.description,
            category_image=category.category_image,
            parent_category_id=parent_id,
            is_active=category.is_active
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        print(f"Category created by {current_user.user_type} {current_user.email}: {db_category.name}")
        
        return db_category
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category: {str(e.orig)}"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )
    
    