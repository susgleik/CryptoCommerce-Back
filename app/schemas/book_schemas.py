# schemas/book_schemas.py
from pydantic import BaseModel, Field, validator
from datetime import date, datetime 
from typing import List, Optional
from decimal import Decimal

class CategoryBase(BaseModel):
    name: str = Field(..., description="Nombre de la categoría")
    description: Optional[str] = Field(None, description="Descripción de la categoría")

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(BaseModel):
    category_id: int = Field(..., description="ID único de la categoría")
    name: str = Field(..., description="Nombre de la categoría")
    description: Optional[str] = Field(None, description="Descripción de la categoría")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "name": "Ficción",
                "description": "Libros de ficción y literatura"
            }
        }

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author_name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    stock: int = Field(0, ge=0)
    isbn: Optional[str] = Field(None, max_length=13)
    publication_date: Optional[date] = None
    category_ids: List[int] = Field(default=[], description="Lista de IDs de categorías")

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor que 0')
        return v

    @validator('stock')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Don Quijote de la Mancha",
                "author_name": "Miguel de Cervantes",
                "price": 29.99,
                "description": "La historia del ingenioso hidalgo...",
                "stock": 100,
                "isbn": "9788401352836",
                "publication_date": "2024-11-04",
                "category_ids": [1, 2]
            }
        }

class BookResponse(BaseModel):
    book_id: int = Field(..., description="ID único del libro")
    title: str = Field(..., description="Título del libro")
    author_name: str = Field(..., description="Nombre del autor")
    price: Decimal = Field(..., description="Precio del libro")
    description: Optional[str] = Field(None, description="Descripción del libro")
    stock: int = Field(..., description="Cantidad disponible en stock")
    isbn: Optional[str] = Field(None, description="ISBN del libro")
    publication_date: Optional[date] = Field(None, description="Fecha de publicación")
    cover_image: Optional[str] = Field(None, description="URL de la imagen de portada")
    created_at: Optional[datetime] = Field(None, description="Fecha y hora de creación del registro")
    updated_at: Optional[datetime] = Field(None, description="Fecha y hora de última actualización")
    categories: List[CategoryResponse] = Field(default=[], description="Lista de categorías del libro")
    
    class Config:
        from_attributes = True
        
class PaginatedBookResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    items_per_page: int
    
#seccion de categorias
#------
#------
