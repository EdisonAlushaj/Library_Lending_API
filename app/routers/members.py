import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Member, Loan
from app.schemas import MemberCreate, MemberUpdate, MemberResponse, PaginatedResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/members", tags=["members"])

@router.get("", response_model=PaginatedResponse[MemberResponse])
def list_members(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    total = db.query(Member).count()
    items = db.query(Member).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total,
            "total_pages": math.ceil(total / page_size) if total else 0}

@router.get("/{id}", response_model=MemberResponse)
def get_member(id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == id).first()
    if not member:
        raise HTTPException(status_code=404, detail={"error": f"Member {id} not found"})
    return member

@router.post("", response_model=MemberResponse, status_code=201)
def create_member(data: MemberCreate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    member = Member(
        full_name=data.full_name,
        email=data.email,
        join_date=data.join_date,
        is_active=data.is_active,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.patch("/{id}", response_model=MemberResponse)
def update_member(id: int, data: MemberUpdate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    member = db.query(Member).filter(Member.id == id).first()
    if not member:
        raise HTTPException(status_code=404, detail={"error": f"Member {id} not found"})
    if data.full_name is not None:
        member.full_name = data.full_name
    if data.email is not None:
        member.email = data.email
    if data.is_active is not None:
        member.is_active = data.is_active
    db.commit()
    db.refresh(member)
    return member

@router.delete("/{id}", status_code=204)
def delete_member(id: int, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    member = db.query(Member).filter(Member.id == id).first()
    if not member:
        raise HTTPException(status_code=404, detail={"error": f"Member {id} not found"})

    # 409 if member has any active loans (return_date IS NULL = still out)
    active_loans = db.query(Loan).filter(
        Loan.member_id == id,
        Loan.return_date == None
    ).count()
    if active_loans > 0:
        raise HTTPException(status_code=409, detail={"error": "Member has active loans"})

    db.delete(member)
    db.commit()
