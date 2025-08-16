# app/models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from ..database.database import Base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

#modelos relacionados con los usuarios
class UserRole(PyEnum):
    COMMON = 'common'
    ADMIN = 'admin'
    STORE_STAFF = 'store_staff'

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    user_type = Column(
        Enum(UserRole, name='user_type_enum'), 
        nullable=False, 
        default=UserRole.COMMON
    )
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp()    
    )
    last_login = Column(DateTime, nullable=True)
    
    # Referencias a otros modelos (estos se definirán en sus respectivos archivos)
    payment_methods = relationship("UserPaymentMethod", back_populates="user", cascade="all, delete-orphan")
    shopping_carts = relationship("ShoppingCart", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("ProductReview", back_populates="user")
    store_staff = relationship("StoreStaff", back_populates="user")
    admin_logs = relationship("AdminActionLog", back_populates="user")
    profile = relationship("UserProfile", uselist=False, back_populates="user")

    
    def __repr__(self):
        return f"<User {self.username}>"
    
    
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id =  Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    address =  Column(Text)
    phone = Column(String(20))
    profile_image = Column(String(255))
    
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile {self.first_name} {self.last_name}>"
    