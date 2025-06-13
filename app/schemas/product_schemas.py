from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    prince: float = Field(..., gt=0)
    description: Optional[str] = None
    online_stock: int = Field(0, ge=0)
    sku: str = Field(..., min_length=30, max_length=50)
    release_date: Optional[datetime] = None
    is_featured: bool = Field(False)
    is_active: bool = Field(True)
    product_type: str = "general"
    attributes: Optional[dict] = None        
    product_image: Optional[str] = None
    
class ProductCreate(ProductBase):
    supplier_id: Optional[int] = None
    category_ids: List[int] = []    
    
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    online_stock: Optional[int] = Field(None, ge=0)
    sku: Optional[str] = Field(None, min_length=3, max_length=50)
    release_date: Optional[date] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    product_type: Optional[str] = None
    attributes: Optional[dict] = None
    product_image: Optional[str] = None
    supplier_id: Optional[int] = None
    category_ids: Optional[List[int]] = None

class ProductResponse(ProductBase):
    product_id: int
    supplier_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category_image: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    category_image: Optional[str] = None
    parent_category_id: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Supplier Schemas
class SupplierBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = None
    supplier_image: Optional[str] = None
    contact_info: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=150)
    description: Optional[str] = None
    supplier_image: Optional[str] = None
    contact_info: Optional[str] = None

class SupplierResponse(SupplierBase):
    supplier_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Product with relationships
class ProductDetailResponse(ProductResponse):
    supplier: Optional[SupplierResponse] = None
    categories: List[CategoryResponse] = []
    
    class Config:
        orm_mode = True

# Product Review Schemas
class ReviewStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProductReviewBase(BaseModel):
    product_id: int
    rating: float = Field(..., ge=1, le=5)
    review_text: Optional[str] = None

class ProductReviewCreate(ProductReviewBase):
    pass

class ProductReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None
    status: Optional[ReviewStatusEnum] = None

class ProductReviewResponse(ProductReviewBase):
    review_id: int
    user_id: int
    created_at: datetime
    status: ReviewStatusEnum
    
    class Config:
        orm_mode = True

# Product Attribute Schemas
class DataTypeEnum(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"

class ProductAttributeTypeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    product_type: str
    data_type: DataTypeEnum
    is_required: bool = False
    is_searchable: bool = False

class ProductAttributeTypeCreate(ProductAttributeTypeBase):
    pass

class ProductAttributeTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    product_type: Optional[str] = None
    data_type: Optional[DataTypeEnum] = None
    is_required: Optional[bool] = None
    is_searchable: Optional[bool] = None

class ProductAttributeTypeResponse(ProductAttributeTypeBase):
    attribute_type_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProductAttributeValueBase(BaseModel):
    product_id: int
    attribute_type_id: int
    text_value: Optional[str] = None
    number_value: Optional[float] = None
    date_value: Optional[date] = None
    boolean_value: Optional[bool] = None

    @validator('text_value', 'number_value', 'date_value', 'boolean_value')
    def validate_value_types(cls, v, values, **kwargs):
        if 'attribute_type_id' in values and values['attribute_type_id']:
            # Aquí se podría agregar validación adicional según el tipo de atributo
            pass
        return v

class ProductAttributeValueCreate(ProductAttributeValueBase):
    pass

class ProductAttributeValueUpdate(BaseModel):
    text_value: Optional[str] = None
    number_value: Optional[float] = None
    date_value: Optional[date] = None
    boolean_value: Optional[bool] = None

class ProductAttributeValueResponse(ProductAttributeValueBase):
    value_id: int
    
    class Config:
        orm_mode = True
    
    

     
    
       