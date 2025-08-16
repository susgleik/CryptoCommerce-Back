from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, ForeignKey, TIMESTAMP, Table, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from ..database.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    supplier_image = Column(String(255))
    contact_info = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, 
                        server_default=func.current_timestamp(),
                        onupdate=func.current_timestamp()
                        )
    
    #relaciones 
    products = relationship("Product", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier {self.name}>"
    

class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.supplier_id', ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL (10,2), nullable=False)
    product_image = Column(String(255))
    description = Column(Text)
    online_stock = Column(Integer, nullable=False, default=0)
    sku = Column(String(50), unique=True, nullable=False)
    release_date = Column(Date)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    product_type = Column(String(100), default='general')
    attributes = Column(JSON)    
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(), 
        onupdate=func.current_timestamp()
    )
    
    supplier = relationship("Supplier", back_populates="products")
    categories = relationship("Category", secondary="product_categories", back_populates="products")
    sales_statistics = relationship("SalesStatistics", back_populates="product", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")
    attribute_values = relationship("ProductAttributeValue", back_populates="product", cascade="all, delete-orphan")
    discounts = relationship("Discount", secondary="product_discounts", back_populates="products")
    
    def __repr__(self):
        return f"<Product {self.name}>"
    
    
class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_image = Column(String(255))
    parent_category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relaciones
    products = relationship("Product", secondary="product_categories", back_populates="categories")
    subcategories = relationship("Category", backref=backref("parent", remote_side=[category_id]))
    discounts = relationship("Discount", secondary="category_discounts", back_populates="categories")
    
    def __repr__(self):
        return f"<Category {self.name}>"
    
    
    
# Tabla de relación muchos a muchos entre productos y categorías
class ProductCategory(Base):
    __tablename__ = "product_categories"
    
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True)
    
    
class ProductReview(Base):
    __tablename__ = "product_reviews"
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    rating = Column(DECIMAL(3, 1), nullable=False)
    review_text = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    status = Column(Enum('pending', 'approved', 'rejected'), default='pending')
    
    # Relaciones
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    
    def __repr__(self):
        return f"<ProductReview {self.review_id}>"


class ProductAttributeType(Base):
    __tablename__ = "product_attribute_types"
    
    attribute_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    product_type = Column(String(100), nullable=False)
    data_type = Column(Enum('text', 'number', 'date', 'boolean'), nullable=False)
    is_required = Column(Boolean, default=False)
    is_searchable = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    values = relationship("ProductAttributeValue", back_populates="attribute_type")
    
    def __repr__(self):
        return f"<ProductAttributeType {self.name}>"


class ProductAttributeValue(Base):
    __tablename__ = "product_attribute_values"
    
    value_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    attribute_type_id = Column(Integer, ForeignKey("product_attribute_types.attribute_type_id", ondelete="CASCADE"), nullable=False)
    text_value = Column(Text)
    number_value = Column(DECIMAL(10, 2))
    date_value = Column(Date)
    boolean_value = Column(Boolean)
    
    # Relaciones
    product = relationship("Product", back_populates="attribute_values")
    attribute_type = relationship("ProductAttributeType", back_populates="values")
    
    def __repr__(self):
        return f"<ProductAttributeValue {self.value_id}>"