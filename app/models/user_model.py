# app/models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Foreingkey
from sqlalchemy.sql import func
from ..database.database import Base
from sqlalchemy.orm import relationship

#modelos relacionados con los usuarios

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    user_type = Column(Enum('common', 'admin', 'store_staff'), nullable=False, default='common')
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp()    
    )
    last_login = Column(DateTime, nullable=True)
    
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    payment_methods = relationship("UserPaymentMethod", back_populates="user", cascade="all, delete-orphan")
    shopping_cart = relationship("ShoppingCart", back_populates="user", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<User {self.username}>"
    
    
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id =  Column(Integer, Foreignkey('users.user_id', ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    address =  Column(Text)
    phone = Column(String(20))
    profile_image = Column(String(255))
    
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile {self.first_name} {self.last_name}>"
    