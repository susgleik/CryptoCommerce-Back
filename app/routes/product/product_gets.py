from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from ...database.database import get_db
from ...models.product_model import Product, Category, Supplier
from ...schemas import product_schemas
from ...core.dependencies import get_current_client_user, get_current_admin_user
from ...models.user_model import User

router = APIRouter()

@router.get(
    "/",
    response_model=List[product_schemas.ProductDetailResponse],
    description="Obtiene una lista de productos con filtros opcionales",
    tags=["Products"]
)
def get_products(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
    name: Optional[str] = Query(None, description="Buscar por nombre del producto"),
    category_id: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    supplier_id: Optional[int] = Query(None, description="Filtrar por ID de proveedor"),
    is_active: Optional[bool] = Query(None, description="Filtrar por productos activos/inactivos"),
    is_featured: Optional[bool] = Query(None, description="Filtrar por productos destacados"),
    product_type: Optional[str] = Query(None, description="Filtrar por tipo de producto"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    in_stock: Optional[bool] = Query(None, description="Filtrar productos con stock disponible")
):
    """
    Obtiene una lista de productos con filtros opcionales y paginación.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar
    - **name**: Buscar productos que contengan este texto en el nombre
    - **category_id**: Filtrar por categoría específica
    - **supplier_id**: Filtrar por proveedor específico
    - **is_active**: Filtrar solo productos activos o inactivos
    - **is_featured**: Filtrar solo productos destacados
    - **product_type**: Filtrar por tipo de producto
    - **min_price**: Precio mínimo
    - **max_price**: Precio máximo
    - **in_stock**: Filtrar solo productos con stock disponible
    """
    
    # query base for products
    query = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    )
    
    # add filters
    filters = []
    
    if name:
        filters.append(Product.name.ilike(f"%{name}%"))
    
    if category_id:
        # check if category exists
        category_exists = db.query(Category).filter(Category.category_id == category_id).first()
        if not category_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        filters.append(Product.categories.any(Category.category_id == category_id))
    
    if supplier_id:
        # check if supplier exists
        supplier_exists = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
        if not supplier_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with ID {supplier_id} not found"
            )
        filters.append(Product.supplier_id == supplier_id)
    
    if is_active is not None:
        filters.append(Product.is_active == is_active)
    
    if is_featured is not None:
        filters.append(Product.is_featured == is_featured)
    
    if product_type:
        filters.append(Product.product_type == product_type)
    
    if min_price is not None:
        filters.append(Product.price >= min_price)
    
    if max_price is not None:
        filters.append(Product.price <= max_price)
        
    if max_price is not None and min_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price"
        )
    
    if in_stock is not None:
        if in_stock:
            filters.append(Product.online_stock > 0)
        else:
            filters.append(Product.online_stock == 0)
    
    # add active filter by default
    if filters:
        query = query.filter(and_(*filters))
    
    # add pagination 
    products = query.offset(skip).limit(limit).all()
    
    return products

        
@router.get(
    "/{product_id}",
    response_model=product_schemas.ProductDetailResponse,
    description="Obtiene un producto específico por su ID",
    tags=["Products"]
)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un producto específico por su ID con toda la información relacionada.
    
    - **product_id**: ID del producto a obtener
    """
    
    product = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    ).filter(Product.product_id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return product


@router.get(
    "/search/{search_term}",
    response_model=List[product_schemas.ProductDetailResponse],
    description="Busca productos por término de búsqueda",
    tags=["Products"]
)
def search_products(
    search_term: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Busca productos por término de búsqueda en nombre y descripción.
    
    - **search_term**: Término a buscar en nombre y descripción
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    """
    
    if len(search_term.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search term must be at least 2 characters long"
        )
    
    # search name and description
    products = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    ).filter(
        and_(
            Product.is_active == True,
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.description.ilike(f"%{search_term}%"),
                Product.sku.ilike(f"%{search_term}%")
            )
        )
    ).offset(skip).limit(limit).all()
    
    return products


@router.get(
    "/featured/",
    response_model=List[product_schemas.ProductDetailResponse],
    description="Obtiene productos destacados",
    tags=["Products"]
)
def get_featured_products(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de productos destacados")
):
    """
    Obtiene productos marcados como destacados.
    
    - **limit**: Número máximo de productos a retornar
    """
    
    products = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    ).filter(
        and_(
            Product.is_featured == True,
            Product.is_active == True
        )
    ).limit(limit).all()
    
    return products


@router.get(
    "/by-category/{category_id}",
    response_model=List[product_schemas.ProductDetailResponse],
    description="Obtiene productos de una categoría específica",
    tags=["Products"]
)
def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Obtiene productos de una categoría específica.
    
    - **category_id**: ID de la categoría
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    """
    
    # cheack if category exists
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    products = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    ).filter(
        and_(
            Product.categories.any(Category.category_id == category_id),
            Product.is_active == True
        )
    ).offset(skip).limit(limit).all()
    
    return products


@router.get(
    "/by-supplier/{supplier_id}",
    response_model=List[product_schemas.ProductDetailResponse],
    description="Obtiene productos de un proveedor específico",
    tags=["Products"]
)
def get_products_by_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Obtiene productos de un proveedor específico.
    
    - **supplier_id**: ID del proveedor
    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a retornar
    """
    
    # Verificar que el proveedor existe
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with ID {supplier_id} not found"
        )
    
    products = db.query(Product).options(
        joinedload(Product.supplier),
        joinedload(Product.categories)
    ).filter(Product.supplier_id == supplier_id).offset(skip).limit(limit).all()
    
    return products    