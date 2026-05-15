import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Book, Author, Loan
from app.schemas import BookCreate, BookUpdate, BookResponse, PaginatedResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=PaginatedResponse[BookResponse])
def list_books(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    total = db.query(Book).count()
    items = (
        db.query(Book)
        .options(joinedload(Book.authors), joinedload(Book.category))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": items, "page": page, "page_size": page_size, "total": total,
            "total_pages": math.ceil(total / page_size) if total else 0}

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db)):
    book = (
        db.query(Book)
        .options(joinedload(Book.authors), joinedload(Book.category))
        .filter(Book.id == id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail={"error": f"Book {id} not found"})
    return book

@router.post("", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    authors = db.query(Author).filter(Author.id.in_(data.author_ids)).all()
    if len(authors) != len(data.author_ids):
        raise HTTPException(status_code=404, detail={"error": "One or more author IDs not found"})

    book = Book(
        title=data.title,
        isbn=data.isbn,
        category_id=data.category_id,
        total_copies=data.total_copies,
        published_year=data.published_year,
        authors=authors,   # SQLAlchemy handles inserting into book_authors
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return db.query(Book).options(joinedload(Book.authors), joinedload(Book.category)).filter(Book.id == book.id).first()

@router.patch("/{id}", response_model=BookResponse)
def update_book(id: int, data: BookUpdate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    book = db.query(Book).options(joinedload(Book.authors)).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail={"error": f"Book {id} not found"})

    if data.title is not None:
        book.title = data.title
    if data.isbn is not None:
        book.isbn = data.isbn
    if data.category_id is not None:
        book.category_id = data.category_id
    if data.total_copies is not None:
        book.total_copies = data.total_copies
    if data.published_year is not None:
        book.published_year = data.published_year
    if data.author_ids is not None:
        authors = db.query(Author).filter(Author.id.in_(data.author_ids)).all()
        book.authors = authors   # replaces the whole author list

    db.commit()
    db.refresh(book)
    return db.query(Book).options(joinedload(Book.authors), joinedload(Book.category)).filter(Book.id == id).first()

@router.delete("/{id}", status_code=204)
def delete_book(id: int, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail={"error": f"Book {id} not found"})

    active_loans = db.query(Loan).filter(
        Loan.book_id == id,
        Loan.return_date == None
    ).count()
    if active_loans > 0:
        raise HTTPException(status_code=409, detail={"error": "Book has active loans"})

    db.delete(book)
    db.commit()