import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Book, Author, book_authors, Loan
from app.schemas import BookCreate, BookUpdate, BookResponse, PaginatedResponse, LoanResponse
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

@router.get("/search", response_model=PaginatedResponse[BookResponse])
def search_books(
    q: str | None = None,
    category_id: int | None = None,
    author_id: int | None = None,
    available_only: bool = False,
    published_after: int | None = None,
    published_before: int | None = None,
    sort_by: str = "title",
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    if sort_by not in ("title", "published_year", "popularity"):
        raise HTTPException(status_code=400, detail={"error": "sort_by must be title, published_year, or popularity"})
    if sort_order not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail={"error": "sort_order must be asc or desc"})

    query = db.query(Book)

    if q:
        query = query.filter(Book.title.ilike(f"%{q}%"))

    if category_id is not None:
        query = query.filter(Book.category_id == category_id)

    if author_id is not None:
        query = query.filter(
            Book.id.in_(
                db.query(book_authors.c.book_id).filter(
                    book_authors.c.author_id == author_id
                )
            )
        )

    if published_after is not None:
        query = query.filter(Book.published_year >= published_after)

    if published_before is not None:
        query = query.filter(Book.published_year <= published_before)

    if available_only:
        active_sq = (
            db.query(Loan.book_id, func.count(Loan.id).label("active_count"))
            .filter(Loan.return_date == None)
            .group_by(Loan.book_id)
            .subquery("active_loans")
        )
        query = query.outerjoin(active_sq, Book.id == active_sq.c.book_id)
        query = query.filter(
            Book.total_copies > func.coalesce(active_sq.c.active_count, 0)
        )

    if sort_by == "popularity":
        pop_sq = (
            db.query(Loan.book_id, func.count(Loan.id).label("loan_count"))
            .group_by(Loan.book_id)
            .subquery("loan_counts")
        )
        query = query.outerjoin(pop_sq, Book.id == pop_sq.c.book_id)
        order_col = func.coalesce(pop_sq.c.loan_count, 0)
    elif sort_by == "published_year":
        order_col = Book.published_year
    else:
        order_col = Book.title

    query = query.order_by(order_col.desc() if sort_order == "desc" else order_col.asc())

    total = query.with_entities(func.count(Book.id.distinct())).scalar()

    items = (
        query
        .options(joinedload(Book.authors), joinedload(Book.category))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }

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

@router.get("/{id}/loan-history", response_model=PaginatedResponse[LoanResponse])
def get_loan_history(id: int, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail={"error": f"Book {id} not found"})

    query = (
        db.query(Loan)
        .options(joinedload(Loan.member), joinedload(Loan.book))
        .filter(Loan.book_id == id)
        .order_by(Loan.loan_date.desc())
    )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }