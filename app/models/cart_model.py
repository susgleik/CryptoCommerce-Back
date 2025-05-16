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

class CartItem(Base):
    __tablename__ = "cart_items"
    
    cart_id = Column(Integer, ForeignKey("shopping_carts.cart_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), primary_key=True)
    quantity = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    cart = relationship("ShoppingCart", back_populates="cart_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<CartItem {self.cart_id}-{self.product_id}>"
class Wishlist(Base):
    __tablename__ = "wishlists"
    
    wishlist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # Relaciones
    user = relationship("User", back_populates="wishlists")
    wishlist_items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wishlist {self.name}>"

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    wishlist_id = Column(Integer, ForeignKey("wishlists.wishlist_id", ondelete="CASCADE"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime, server_default=func.current_timestamp())
    notes = Column(Text)
    
    # Relaciones
    wishlist = relationship("Wishlist", back_populates="wishlist_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<WishlistItem {self.wishlist_id}-{self.product_id}>"    

    
    