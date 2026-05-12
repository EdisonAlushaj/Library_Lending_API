from sqlalchemy import (
    Column, Integer, String, Boolean, Date, ForeignKey,
    Table, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base

book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index = True)
    full_name = Column(String, nullable=False)
    email = Column(String,unique=True, index=True, nullable=False)
    jopin_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    loans = relationship("Loan", back_populates="member")

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    country = Column(String, nullable=False)

    books = relationship("Book", secondary=book_authors, back_populates="authors")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    books = relationship("Book", back_populates="category")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    published_year = Column(Integer, nullable=False)

    category = relationship("Category", back_populates="books")
    authors = relationship("Author", secondary=book_authors, back_populates="books")
    loans = relationship("Loan", back_populates="book")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    loan_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)   # NULL means the loan is still active

    member = relationship("Member", back_populates="loans")
    book = relationship("Book", back_populates="loans")


    