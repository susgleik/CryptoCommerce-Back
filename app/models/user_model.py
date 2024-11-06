# app/models/user_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from ..database.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum('common', 'admin'), nullable=False, default='common')
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime, 
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp()
    )
    
    def __repr__(self):
        return f"<User {self.username}>"