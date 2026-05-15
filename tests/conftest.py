import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["API_KEY"] = "testkey"

from app.main import app
from app.database import Base, get_db
from app.models import Category, Author, Book, Member

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture()
def category(db):
    cat = Category(name="Fiction")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@pytest.fixture()
def author(db):
    a = Author(full_name="Test Author", country="Albania")
    db.add(a)
    db.commit()
    db.refresh(a)
    return a

@pytest.fixture()
def book(db, category, author):
    b = Book(
        title="Test Book",
        isbn="1234567890",
        category_id=category.id,
        total_copies=3,
        published_year=2020,
        authors=[author],
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@pytest.fixture()
def member(db):
    m = Member(
        full_name="Test Member",
        email="test@example.com",
        join_date=date.today(),
        is_active=True,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m