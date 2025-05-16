from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.database import Base

class SalesStatistics(Base):
    __tablename__ = "sales_statistics"
    
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    total_online_sales = Column(Integer, default=0)
    total_physical_sales = Column(Integer, default=0)
    online_revenue = Column(DECIMAL(12, 2), default=0.00)
    physical_revenue = Column(DECIMAL(12, 2), default=0.00)
    views_count = Column(Integer, default=0)
    conversion_rate = Column(DECIMAL(5, 2), default=0.00)
    last_updated = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relaciones
    product = relationship("Product", back_populates="sales_statistics")
    
    def __repr__(self):
        return f"<SalesStatistics {self.stat_id}>"


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    
    movement_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    movement_type = Column(Enum('entrada', 'salida', 'transferencia', 'ajuste', 'online_reserva'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reference = Column(String(100))
    reason = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    product = relationship("Product")
    store = relationship("Store")
    user = relationship("User")
    
    def __repr__(self):
        return f"<InventoryMovement {self.movement_id}>"


class AdminActionLog(Base):
    __tablename__ = "admin_actions_log"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    ip_address = Column(String(45))
    
    # Relaciones
    user = relationship("User", back_populates="admin_logs")
    
    def __repr__(self):
        return f"<AdminActionLog {self.log_id}>"