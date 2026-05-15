from datetime import date
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Category
class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryResponse(ORMBase):
    id: int
    name: str

# Author
class AuthorCreate(BaseModel):
    full_name: str
    country: str

class AuthorUpdate(BaseModel):
    full_name: Optional[str] = None
    country: Optional[str] = None

class AuthorResponse(ORMBase):
    id: int
    full_name: str
    country: str

# Member
class MemberCreate(BaseModel):
    full_name: str
    email: str
    join_date: date
    is_active: bool = True

class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class MemberResponse(ORMBase):
    id: int
    full_name: str
    email: str
    join_date: date
    is_active: bool

# Book
class BookCreate(BaseModel):
    title: str
    isbn: str
    category_id: int
    total_copies: int
    published_year: int
    author_ids: list[int]

class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    category_id: Optional[int] = None
    total_copies: Optional[int] = None
    published_year: Optional[int] = None
    author_ids: Optional[list[int]] = None

class BookResponse(ORMBase):
    id: int
    title: str
    isbn: str
    total_copies: int
    published_year: int
    category: CategoryResponse          
    authors: list[AuthorResponse]       

#Pagfination wrapper
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

# Loan
class LoanMemberInfo(ORMBase):
    id: int
    full_name: str

class LoanBookInfo(ORMBase):
    id: int
    title: str

class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    due_date: date

class LoanResponse(ORMBase):
    id: int
    member_id: int
    book_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date]
    member: LoanMemberInfo
    book: LoanBookInfo

# Reports
class TopBorrowerResponse(BaseModel):
    id: int
    full_name: str
    email: str
    join_date: date
    is_active: bool
    total_loans: int

class OverdueLoanResponse(BaseModel):
    id: int
    member_name: str
    book_title: str
    due_date: date
    days_overdue: int