# models/book_model.py
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Date, ForeignKey, TIMESTAMP, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.database import Base

book_categories = Table(
    'book_categories',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.book_id', ondelete="CASCADE")),
    Column('category_id', Integer, ForeignKey('categories.category_id', ondelete="CASCADE")),
    extend_existing=True
)

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relación many-to-many con books
    books = relationship("Book", secondary=book_categories, back_populates="categories")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Book(Base):
    __tablename__ = "books"
    __table_args__ = {'extend_existing': True}
    
    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author_name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    cover_image = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    isbn = Column(String(13), nullable=True)
    publication_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)
    
    # Relación many-to-many con categories
    categories = relationship("Category", secondary=book_categories, back_populates="books")