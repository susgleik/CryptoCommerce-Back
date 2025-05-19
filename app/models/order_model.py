from sqlalchemy import Column, Integer, Enum, DateTime, Text, String, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base
class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    payment_type_id = Column(Integer, ForeignKey("payment_methods.payment_type_id"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum('pending', 'processing', 'paid', 'shipped', 'delivered', 'cancelled'), default='pending')
    shipping_address = Column(Text, nullable=False)
    tracking_number = Column(String(100))
    delivery_method = Column(Enum('shipping', 'store_pickup'), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relaciones
    user = relationship("User", back_populates="orders")
    payment_type = relationship("PaymentMethod", back_populates="orders")
    store = relationship("Store")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_id}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(DECIMAL(10, 2), nullable=False)
    
    # Relaciones
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem {self.order_id}-{self.product_id}>"