from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class Discount(Base):
    __tablename__ = "discounts"
    
    discount_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    discount_type = Column(Enum('percentage', 'fixed_amount'), nullable=False)
    discount_value = Column(DECIMAL(10, 2), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    min_purchase = Column(DECIMAL(10, 2), default=0.00)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    coupon_code = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    products = relationship("Product", secondary="product_discounts", back_populates="discounts")
    categories = relationship("Category", secondary="category_discounts", back_populates="discounts")
    
    def __repr__(self):
        return f"<Discount {self.name}>"


# Tabla de relación entre productos y descuentos
class ProductDiscount(Base):
    __tablename__ = "product_discounts"
    
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    discount_id = Column(Integer, ForeignKey("discounts.discount_id", ondelete="CASCADE"), primary_key=True)


# Tabla de relación entre categorías y descuentos
class CategoryDiscount(Base):
    __tablename__ = "category_discounts"
    
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True)
    discount_id = Column(Integer, ForeignKey("discounts.discount_id", ondelete="CASCADE"), primary_key=True)