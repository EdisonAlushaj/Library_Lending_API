import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, PaginatedResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=PaginatedResponse[CategoryResponse])
def get_categories(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    total = db.query(Category).count()
    items = db.query(Category).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }

@router.get("/{id}", response_model=CategoryResponse)
def get_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    category = Category(name=data.name)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": f"Category '{data.name}' already exists"})
    db.refresh(category)
    return category

@router.patch("/{id}", response_model=CategoryResponse)
def update_category(id: int, data: CategoryUpdate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail={"error": f"Category {id} not found"})
    if data.name is not None:
        category.name = data.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"error": f"Category '{data.name}' already exists"})
    db.refresh(category)
    return category

@router.delete("/{id}", status_code=204)
def delete_category(id: int, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail={"error": f"Category {id} not found"})
    db.delete(category)
    db.commit()