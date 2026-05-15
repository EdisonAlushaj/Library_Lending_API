import math
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Loan, Member, Book
from app.schemas import LoanCreate, LoanResponse, PaginatedResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/loans", tags=["loans"])

def get_loan_or_404(id: int, db: Session) -> Loan:
    loan = (
        db.query(Loan)
        .options(joinedload(Loan.member), joinedload(Loan.book))
        .filter(Loan.id == id)
        .first()
    )
    if not loan:
        raise HTTPException(status_code=404, detail={"error": f"Loan {id} not found"})
    return loan


@router.get("", response_model=PaginatedResponse[LoanResponse])
def list_loans(
    member_id: int | None = None,
    book_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    today = date.today()
    query = db.query(Loan).options(joinedload(Loan.member), joinedload(Loan.book))

    if member_id is not None:
        query = query.filter(Loan.member_id == member_id)
    if book_id is not None:
        query = query.filter(Loan.book_id == book_id)

    if status == "active":
        query = query.filter(Loan.return_date == None, Loan.due_date >= today)
    elif status == "returned":
        query = query.filter(Loan.return_date != None)
    elif status == "overdue":
        query = query.filter(Loan.return_date == None, Loan.due_date < today)
    elif status is not None:
        raise HTTPException(status_code=400, detail={"error": "status must be active, returned, or overdue"})

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }

@router.post("", response_model=LoanResponse, status_code=201)
def borrow_book(data: LoanCreate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail={"error": f"Member {data.member_id} not found"})

    if not member.is_active:
        raise HTTPException(status_code=400, detail={"error": "Member is not active"})

    book = db.query(Book).filter(Book.id == data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail={"error": f"Book {data.book_id} not found"})

    active_loans_count = db.query(Loan).filter(
        Loan.book_id == data.book_id,
        Loan.return_date == None,
    ).count()

    if book.total_copies <= active_loans_count:
        raise HTTPException(status_code=409, detail={"error": "No copies available"})

    loan = Loan(
        member_id=data.member_id,
        book_id=data.book_id,
        loan_date=date.today(),
        due_date=data.due_date,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return get_loan_or_404(loan.id, db)

@router.post("/{id}/return", response_model=LoanResponse)
def return_book(id: int, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    loan = get_loan_or_404(id, db)

    if loan.return_date is not None:
        raise HTTPException(status_code=409, detail={"error": "Loan already returned"})

    loan.return_date = date.today()
    db.commit()
    db.refresh(loan)
    return get_loan_or_404(loan.id, db)