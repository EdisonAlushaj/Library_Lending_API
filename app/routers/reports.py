from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models import Member, Loan, Book
from app.schemas import TopBorrowerResponse, OverdueLoanResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-borrowers", response_model=list[TopBorrowerResponse])
def top_borrowers(limit: int = 5, db: Session = Depends(get_db)):
    results = (
        db.query(Member, func.count(Loan.id).label("total_loans"))
        .join(Loan, Member.id == Loan.member_id)
        .group_by(Member.id)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": member.id,
            "full_name": member.full_name,
            "email": member.email,
            "join_date": member.join_date,
            "is_active": member.is_active,
            "total_loans": total_loans
        } 
        for member, total_loans in results
    ]

@router.get("/overdue-loans", response_model=list[OverdueLoanResponse])
def overdue_loans(db: Session = Depends(get_db)):
    today = date.today()

    loans = (
        db.query(Loan)
        .options(joinedload(Loan.member), joinedload(Loan.book))
        .filter(Loan.return_date == None, Loan.due_date < today)
        .all()
    )

    return [
        {
            "id": loan.id,
            "member_name": loan.member.full_name,
            "book_title": loan.book.title,
            "due_date": loan.due_date,
            "days_overdue": (today - loan.due_date).days,
        }
        for loan in loans
    ]