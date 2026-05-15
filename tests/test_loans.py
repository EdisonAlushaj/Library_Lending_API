from datetime import date, timedelta

HEADERS = {"X-API-Key": "testkey"}
DUE = str(date.today() + timedelta(days=14))

def test_borrow_success(client, member, book):
    res = client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)
    assert res.status_code == 201
    data = res.json()
    assert data["member_id"] == member.id
    assert data["book_id"] == book.id
    assert data["return_date"] is None

def test_borrow_inactive_member(client, member, book, db):
    member.is_active = False
    db.commit()

    res = client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)
    assert res.status_code == 400

def test_borrow_no_copies(client, member, book, db):
    book.total_copies = 1
    db.commit()

    client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)

    res = client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)
    assert res.status_code == 409

def test_return_flow(client, member, book):
    borrow = client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)
    loan_id = borrow.json()["id"]

    ret = client.post(f"/api/v1/loans/{loan_id}/return", headers=HEADERS)
    assert ret.status_code == 200
    assert ret.json()["return_date"] is not None

def test_double_return(client, member, book):
    borrow = client.post("/api/v1/loans", json={
        "member_id": member.id,
        "book_id": book.id,
        "due_date": DUE,
    }, headers=HEADERS)
    loan_id = borrow.json()["id"]

    client.post(f"/api/v1/loans/{loan_id}/return", headers=HEADERS)
    res = client.post(f"/api/v1/loans/{loan_id}/return", headers=HEADERS)
    assert res.status_code == 409
