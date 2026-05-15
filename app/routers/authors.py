import math
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Author
from app.schemas import AuthorCreate, AuthorUpdate, AuthorResponse, PaginatedResponse
from app.auth import verify_api_key

router = APIRouter(prefix="/authors", tags=["authors"])

@router.get("", response_model=PaginatedResponse[AuthorResponse])
def get_authors(page: int=1, page_size: int=20, db: Session = Depends(get_db)):
    total = db.query(Author).count()
    items = db.query(Author).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0
        }

@router.get("/{id}", response_model=AuthorResponse)
def get_author(id: int, db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.id == id).first()

    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@router.post("", response_model=AuthorResponse, status_code=201)
def create_author(data: AuthorCreate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    author = Author(full_name=data.full_name, country=data.country)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.patch("/{id}", response_model=AuthorResponse)
def update_author(id: int, data: AuthorUpdate, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    author = db.query(Author).filter(Author.id == id).first()
    if not author:
        raise HTTPException(status_code=404, detail={"error": f"Author {id} not found"})
    if data.full_name is not None:
        author.full_name = data.full_name
    if data.country is not None:
        author.country = data.country
    db.commit()
    db.refresh(author)
    return author

@router.delete("/{id}", status_code=204)
def delete_author(id: int, db: Session = Depends(get_db), _=Depends(verify_api_key)):
    author = db.query(Author).filter(Author.id == id).first()
    if not author:
        raise HTTPException(status_code=404, detail={"error": f"Author {id} not found"})
    db.delete(author)
    db.commit()