from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Foreingkey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class PayMethod(base):
    __tablename__ = "payment_methods"
    
    payment_payment_type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False) 
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    user_payment_methods = relationship("UserPaymentMethod", back_populates="payment_type")
    
    def __repr__(self):
        return f"<paymentMethod {self.name}>"
    
    
class UserPaymentMethod(Base):
    __tablename__ = "user_payment_methods"
    
    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, Foreingkey("users.user_id", ondelete="CASCADE"), nullable=False)
    payment_type_id = Column(Integer, Foreingkey("payment_methods.payment_type_id", ondelete="CASCADE"), nullable=False)
    account_details = Column(String(225), nullable=False) # Encriptar en la aplicacion 
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    expires_at = Column(DateTime, nullable=True)
    
    payment_type = relationship("payMethod", back_populates="user_payment_methods")
    user = relationship("User", back_populates="payment_methods")
    
    
    def __repr__(self):
        return f"<UserPaymentMethod {self.user_id} {self.payment_type_id}>"
    
    
    
    