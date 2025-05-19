from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    payment_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    user_payment_methods = relationship("UserPaymentMethod", back_populates="payment_type")
    orders = relationship("Order", back_populates="payment_type")
    
    def __repr__(self):
        return f"<PaymentMethod {self.name}>"
    
    
class UserPaymentMethod(Base):
    __tablename__ = "user_payment_methods"
    
    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    payment_type_id = Column(Integer, ForeignKey("payment_methods.payment_type_id"), nullable=False)
    account_details = Column(String(255), nullable=False)  # Debe encriptarse en la aplicación
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    expires_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="payment_methods")
    payment_type = relationship("PaymentMethod", back_populates="user_payment_methods")
    
    def __repr__(self):
        return f"<UserPaymentMethod {self.payment_method_id}>"
    
    
    
    