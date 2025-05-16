from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Time, ForeignKey, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class Store(Base):
    __tablename__ = "stores"
    
    store_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(20))
    email = Column(String(150))
    opening_hours = Column(Time)
    closing_hours = Column(Time)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relaciones
    inventory = relationship("StoreInventory", back_populates="store", cascade="all, delete-orphan")
    staff = relationship("StoreStaff", back_populates="store")
    physical_sales = relationship("PhysicalSale", back_populates="store")
    
    def __repr__(self):
        return f"<Store {self.name}>"


class StoreInventory(Base):
    __tablename__ = "store_inventory"
    
    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String(50))
    low_stock_threshold = Column(Integer, default=5)
    notify_low_stock = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    store = relationship("Store", back_populates="inventory")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<StoreInventory {self.store_id}-{self.product_id}>"


class StoreStaff(Base):
    __tablename__ = "store_staff"
    
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    role = Column(Enum('manager', 'cashier', 'inventory'), nullable=False)
    hire_date = Column(DateTime, server_default=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    user = relationship("User", back_populates="store_staff")
    store = relationship("Store", back_populates="staff")
    
    def __repr__(self):
        return f"<StoreStaff {self.staff_id}>"


class PhysicalSale(Base):
    __tablename__ = "physical_sales"
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('efectivo', 'tarjeta', 'otro'), nullable=False)
    receipt_number = Column(String(50), nullable=False)
    is_invoice_required = Column(Boolean, default=False)
    customer_tax_info = Column(String(150))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    store = relationship("Store", back_populates="physical_sales")
    user = relationship("User")
    sale_items = relationship("PhysicalSaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PhysicalSale {self.sale_id}>"


class PhysicalSaleItem(Base):
    __tablename__ = "physical_sale_items"
    
    sale_id = Column(Integer, ForeignKey("physical_sales.sale_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Relaciones
    sale = relationship("PhysicalSale", back_populates="sale_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<PhysicalSaleItem {self.sale_id}-{self.product_id}>"


class StoreInventory(Base):
    __tablename__ = "store_inventory"
    
    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    shelf_location = Column(String(50))
    low_stock_threshold = Column(Integer, default=5)
    notify_low_stock = Column(Boolean, default=True)
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    store = relationship("Store", back_populates="inventory")
    book = relationship("Book")
    
    def __repr__(self):
        return f"<StoreInventory {self.store_id}-{self.book_id}>"


class StoreStaff(Base):
    __tablename__ = "store_staff"
    
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    role = Column(Enum('manager', 'cashier', 'inventory'), nullable=False)
    hire_date = Column(DateTime, server_default=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    user = relationship("User", back_populates="store_staff")
    store = relationship("Store", back_populates="staff")
    
    def __repr__(self):
        return f"<StoreStaff {self.staff_id}>"


class PhysicalSale(Base):
    __tablename__ = "physical_sales"
    
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('efectivo', 'tarjeta', 'otro'), nullable=False)
    receipt_number = Column(String(50), nullable=False)
    is_invoice_required = Column(Boolean, default=False)
    customer_tax_info = Column(String(150))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    store = relationship("Store", back_populates="physical_sales")
    user = relationship("User")
    sale_items = relationship("PhysicalSaleItem", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PhysicalSale {self.sale_id}>"


class PhysicalSaleItem(Base):
    __tablename__ = "physical_sale_items"
    
    sale_id = Column(Integer, ForeignKey("physical_sales.sale_id", ondelete="CASCADE"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Relaciones
    sale = relationship("PhysicalSale", back_populates="sale_items")
    book = relationship("Book")
    
    def __repr__(self):
        return f"<PhysicalSaleItem {self.sale_id}-{self.book_id}>"