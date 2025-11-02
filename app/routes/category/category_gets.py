from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from ...database.database import get_db
from ...models.product_model import Category, Product
from ...schemas import product_schemas

router = APIRouter()

@router.get(
    "/",
    response_model=List[product_schemas.CategoryResponse],
    description="Obtiene una lista de categorías con filtros opcionales",
    tags=["Categories"]
)
def get_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
    name: Optional[str] = Query(None, description="Buscar por nombre de la categoría"),
    is_active: Optional[bool] = Query(None, description="Filtrar por categorías activas/inactivas"),
    parent_category_id: Optional[int] = Query(None, description="Filtrar por categoría padre")
):
    """
    Obtiene una lista de categorías con filtros opcionales y paginación.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar
    - **name**: Buscar categorías que contengan este texto en el nombre
    - **is_active**: Filtrar solo categorías activas o inactivas
    - **parent_category_id**: Filtrar por categoría padre específica
    """
    
    query = db.query(Category)
    filters = []
    
    if name:
        filters.append(Category.name.ilike(f"%{name}%"))
    
    if is_active is not None:
        filters.append(Category.is_active == is_active)
    
    if parent_category_id is not None:
        parent_exists = db.query(Category).filter(
            Category.category_id == parent_category_id
        ).first()
        
        if not parent_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with ID {parent_category_id} not found"
            )
        
        filters.append(Category.parent_category_id == parent_category_id)
    
    if filters:
        query = query.filter(and_(*filters))
    
    categories = query.offset(skip).limit(limit).all()
    
    return categories


@router.get(
    "/{category_id}",
    response_model=product_schemas.CategoryResponse,
    description="Obtiene una categoría específica por su ID",
    tags=["Categories"]
)
def get_category_by_id(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una categoría específica por su ID.
    
    - **category_id**: ID de la categoría a obtener
    """
    
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return category


@router.get(
    "/{category_id}/subcategories",
    response_model=List[product_schemas.CategoryResponse],
    description="Obtiene las subcategorías de una categoría",
    tags=["Categories"]
)
def get_subcategories(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(None, description="Filtrar por subcategorías activas/inactivas")
):
    """
    Obtiene las subcategorías de una categoría específica.
    
    - **category_id**: ID de la categoría padre
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    - **is_active**: Filtrar solo subcategorías activas o inactivas
    """
    
    parent_category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not parent_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent category with ID {category_id} not found"
        )
    
    query = db.query(Category).filter(
        Category.parent_category_id == category_id
    )
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    subcategories = query.offset(skip).limit(limit).all()
    
    return subcategories


@router.get(
    "/root/all",
    response_model=List[product_schemas.CategoryResponse],
    description="Obtiene las categorías raíz (sin padre)",
    tags=["Categories"]
)
def get_root_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = Query(True, description="Filtrar por categorías activas/inactivas")
):
    """
    Obtiene las categorías raíz (que no tienen categoría padre).
    
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    - **is_active**: Filtrar solo categorías activas o inactivas (default: True)
    """
    
    query = db.query(Category).filter(
        Category.parent_category_id.is_(None)
    )
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    categories = query.offset(skip).limit(limit).all()
    
    return categories


@router.get(
    "/search/{search_term}",
    response_model=List[product_schemas.CategoryResponse],
    description="Busca categorías por término de búsqueda",
    tags=["Categories"]
)
def search_categories(
    search_term: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = Query(True, description="Filtrar por categorías activas")
):
    """
    Busca categorías por término de búsqueda en nombre y descripción.
    
    - **search_term**: Término a buscar en nombre y descripción
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    - **is_active**: Filtrar solo categorías activas (default: True)
    """
    
    if len(search_term.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search term must be at least 2 characters long"
        )
    
    query = db.query(Category).filter(
        or_(
            Category.name.ilike(f"%{search_term}%"),
            Category.description.ilike(f"%{search_term}%")
        )
    )
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    categories = query.offset(skip).limit(limit).all()
    
    return categories


@router.get(
    "/{category_id}/products-count",
    response_model=dict,
    description="Obtiene el conteo de productos en una categoría",
    tags=["Categories"]
)
def get_category_products_count(
    category_id: int,
    db: Session = Depends(get_db),
    include_inactive: bool = Query(False, description="Incluir productos inactivos en el conteo")
):
    """
    Obtiene el conteo de productos asociados a una categoría.
    
    - **category_id**: ID de la categoría
    - **include_inactive**: Incluir productos inactivos en el conteo (default: False)
    """
    
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    query = db.query(Product).filter(
        Product.categories.any(Category.category_id == category_id)
    )
    
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    
    products_count = query.count()
    
    return {
        "category_id": category_id,
        "category_name": category.name,
        "products_count": products_count,
        "include_inactive": include_inactive
    }


@router.get(
    "/{category_id}/tree",
    response_model=dict,
    description="Obtiene el árbol jerárquico de una categoría",
    tags=["Categories"]
)
def get_category_tree(
    category_id: int,
    db: Session = Depends(get_db),
    max_depth: int = Query(3, ge=1, le=10, description="Profundidad máxima del árbol")
):
    """
    Obtiene el árbol jerárquico de una categoría, incluyendo sus subcategorías.
    
    - **category_id**: ID de la categoría raíz
    - **max_depth**: Profundidad máxima del árbol (default: 3, max: 10)
    """
    
    def build_tree(category, current_depth=0):
        """Función recursiva para construir el árbol de categorías"""
        if current_depth >= max_depth:
            return None
        
        tree = {
            "category_id": category.category_id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active,
            "subcategories": []
        }
        
        subcategories = db.query(Category).filter(
            Category.parent_category_id == category.category_id,
            Category.is_active == True
        ).all()
        
        for subcat in subcategories:
            subtree = build_tree(subcat, current_depth + 1)
            if subtree:
                tree["subcategories"].append(subtree)
        
        return tree
    
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return build_tree(category)