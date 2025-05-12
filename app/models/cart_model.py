from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.database import Base

class ShoppingCart(Base):
    __tablename__ = "shopping_carts"
    
    cart_id = Column(Integer, primary_key=True, autoIncrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())  
    updated_at = Column(DateTime, 
                        server_default=func.current_timestamp(), 
                        onupdate=func.current_timestamp())
    
    user = relationship("User", back_populates="shopping_cart")
    
    def __repr__(self):
        return f"<ShoppingCart {self.cart_id}>"

    
    