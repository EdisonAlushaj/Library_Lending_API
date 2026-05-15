from datetime import date, timedelta
from app.models import Book

HEADERS = {"X-API-Key": "testkey"}

def test_search_pagination_shape(client, book):
    res = client.get("/api/v1/books/search")
    assert res.status_code == 200
    data = res.json()
    for key in ("items", "page", "page_size", "total", "total_pages"):
        assert key in data

def test_search_by_title(client, db, category, author):
    b1 = Book(title="Python Basics", isbn="111", category_id=category.id,
              total_copies=1, published_year=2020, authors=[author])
    b2 = Book(title="Advanced SQL", isbn="222", category_id=category.id,
              total_copies=1, published_year=2021, authors=[author])
    db.add_all([b1, b2])
    db.commit()

    res = client.get("/api/v1/books/search?q=python")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Python Basics"

def test_search_available_only(client, db, member, book):
    book.total_copies = 1
    db.commit()

    client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": str(date.today() + timedelta(days=14)),
    }, headers=HEADERS)

    res = client.get("/api/v1/books/search?available_only=true")
    assert res.status_code == 200
    assert res.json()["total"] == 0
