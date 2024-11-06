# routes/books.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.database import get_db
from ..models.book_model import Book  # Removidas las importaciones de Author y Category
from ..schemas import book_schemas
from ..models.user_model import User 
from ..auth.dependencies import get_current_user, get_current_admin
from fastapi.security import HTTPBearer
from ..auth.jwt_handler import security
import logging
from decimal import Decimal
from ..models.book_model import Book, Category  # Añadida la importación de Category


router = APIRouter()
# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/books/", 
    response_model=book_schemas.BookResponse,
    summary="Crear un nuevo libro",
    description="Crea un nuevo libro con la información proporcionada."
)
async def create_book(
    book: book_schemas.BookCreate,
    db: Session = Depends(get_db),
    token: str = Depends(security)
):
    try:
        logger.info(f"Intentando crear libro: {book.title}")
        
        # Validar el precio
        if not isinstance(book.price, (int, float, Decimal)) or book.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio debe ser un número mayor que 0"
            )

        # Validar el stock
        if book.stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El stock no puede ser negativo"
            )

        # Verificar categorías si se proporcionan
        categories = []
        if book.category_ids:
            for category_id in book.category_ids:
                category = db.query(Category).filter(Category.category_id == category_id).first()
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Categoría con id {category_id} no encontrada"
                    )
                categories.append(category)

        # Crear el libro
        try:
            db_book = Book(
                title=book.title,
                author_name=book.author_name,
                price=book.price,
                description=book.description,
                stock=book.stock,
                isbn=book.isbn,
                publication_date=book.publication_date,
                categories=categories
            )
            
            db.add(db_book)
            db.commit()
            db.refresh(db_book)
            
            logger.info(f"Libro creado exitosamente: {db_book.title}")
            return db_book
            
        except Exception as e:
            logger.error(f"Error al crear el libro: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear el libro: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/books/", response_model=book_schemas.PaginatedBookResponse)
async def get_books(
    page: int = Query(1, gt=0),
    items_per_page: int = Query(10, gt=0, le=100),
    search: Optional[str] = None,
    author_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Book)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(Book.title.ilike(search_term))
    
    if author_name:
        author_search = f"%{author_name}%"
        query = query.filter(Book.author_name.ilike(author_search))
    
    total = query.count()
    skip = (page - 1) * items_per_page
    books = query.offset(skip).limit(items_per_page).all()
    
    return {
        "items": books,
        "total": total,
        "page": page,
        "items_per_page": items_per_page
    }

@router.get("/books/{book_id}", response_model=book_schemas.BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.put("/books/{book_id}", response_model=book_schemas.BookResponse)
async def update_book(
    book_id: int,
    book_update: book_schemas.BookCreate,
    db: Session = Depends(get_db),
    credentials: HTTPBearer = Security(security)
):
    db_book = db.query(Book).filter(Book.book_id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Actualizar los campos del libro
    for var, value in vars(book_update).items():
        if value is not None:
            setattr(db_book, var, value)
    
    db.commit()
    db.refresh(db_book)
    
    return db_book

@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}


# Endpoints para categorías
#-----
#-----
@router.get(
    "/categories",
    response_model=List[book_schemas.CategoryResponse],
    summary="Listar categorías",
    description="Obtiene la lista de todas las categorías disponibles"
)
async def get_categories(
    db: Session = Depends(get_db)
):
    try:
        logger.info("Obteniendo lista de categorías")
        categories = db.query(Category).all()
        return categories
    except Exception as e:
        logger.error(f"Error al obtener categorías: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las categorías: {str(e)}"
        )