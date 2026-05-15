import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, timedelta
from app.database import SessionLocal
from app.models import Member, Author, Category, Book, Loan, book_authors

def seed():
    db = SessionLocal()

    try:
        # ── Clear existing data (order matters — FK constraints) ──
        db.execute(book_authors.delete())
        db.query(Loan).delete()
        db.query(Book).delete()
        db.query(Author).delete()
        db.query(Category).delete()
        db.query(Member).delete()
        db.commit()

        # ── Categories ────────────────────────────────────────────
        fiction    = Category(name="Fiction")
        science    = Category(name="Science")
        history    = Category(name="History")
        technology = Category(name="Technology")
        db.add_all([fiction, science, history, technology])
        db.commit()

        # ── Authors ───────────────────────────────────────────────
        orwell   = Author(full_name="George Orwell",       country="United Kingdom")
        rowling  = Author(full_name="J.K. Rowling",        country="United Kingdom")
        hawking  = Author(full_name="Stephen Hawking",     country="United Kingdom")
        christie = Author(full_name="Agatha Christie",     country="United Kingdom")
        harari   = Author(full_name="Yuval Noah Harari",   country="Israel")
        herbert  = Author(full_name="Frank Herbert",       country="United States")
        sagan    = Author(full_name="Carl Sagan",          country="United States")
        asimov   = Author(full_name="Isaac Asimov",        country="United States")
        gladwell = Author(full_name="Malcolm Gladwell",    country="Canada")
        martin   = Author(full_name="Robert C. Martin",   country="United States")
        db.add_all([orwell, rowling, hawking, christie, harari, herbert, sagan, asimov, gladwell, martin])
        db.commit()

        # ── Books (20+, some with multiple authors) ───────────────
        books = [
            # Fiction
            Book(title="1984",                        isbn="9780451524935", category=fiction,    total_copies=4, published_year=1949, authors=[orwell]),
            Book(title="Animal Farm",                 isbn="9780451526342", category=fiction,    total_copies=3, published_year=1945, authors=[orwell]),
            Book(title="Harry Potter and the Philosopher's Stone", isbn="9780747532699", category=fiction, total_copies=5, published_year=1997, authors=[rowling]),
            Book(title="Harry Potter and the Chamber of Secrets",  isbn="9780747538486", category=fiction, total_copies=4, published_year=1998, authors=[rowling]),
            Book(title="Dune",                        isbn="9780441013593", category=fiction,    total_copies=3, published_year=1965, authors=[herbert]),
            Book(title="Foundation",                  isbn="9780553293357", category=fiction,    total_copies=2, published_year=1951, authors=[asimov]),
            Book(title="And Then There Were None",    isbn="9780062073488", category=fiction,    total_copies=3, published_year=1939, authors=[christie]),
            Book(title="Murder on the Orient Express",isbn="9780062073501", category=fiction,    total_copies=2, published_year=1934, authors=[christie]),

            # Science (some with multiple authors)
            Book(title="A Brief History of Time",     isbn="9780553380163", category=science,    total_copies=4, published_year=1988, authors=[hawking]),
            Book(title="Cosmos",                      isbn="9780345539434", category=science,    total_copies=3, published_year=1980, authors=[sagan]),
            Book(title="Pale Blue Dot",               isbn="9780345376596", category=science,    total_copies=2, published_year=1994, authors=[sagan]),
            Book(title="Sapiens",                     isbn="9780062316097", category=science,    total_copies=5, published_year=2011, authors=[harari]),
            Book(title="Homo Deus",                   isbn="9780062464316", category=science,    total_copies=3, published_year=2015, authors=[harari]),
            Book(title="The Grand Design",            isbn="9780553805376", category=science,    total_copies=2, published_year=2010, authors=[hawking, sagan]),   # multiple authors

            # History
            Book(title="The Art of War",              isbn="9781599869773", category=history,    total_copies=3, published_year=500,  authors=[]),
            Book(title="Guns Germs and Steel",        isbn="9780393317558", category=history,    total_copies=2, published_year=1997, authors=[]),
            Book(title="The Silk Roads",              isbn="9781101912379", category=history,    total_copies=2, published_year=2015, authors=[]),

            # Technology (some with multiple authors)
            Book(title="Clean Code",                  isbn="9780132350884", category=technology, total_copies=4, published_year=2008, authors=[martin]),
            Book(title="The Tipping Point",           isbn="9780316346627", category=technology, total_copies=3, published_year=2000, authors=[gladwell]),
            Book(title="Outliers",                    isbn="9780316017923", category=technology, total_copies=3, published_year=2008, authors=[gladwell]),
            Book(title="The Pragmatic Programmer",    isbn="9780135957059", category=technology, total_copies=2, published_year=2019, authors=[martin, gladwell]),  # multiple authors
            Book(title="Cosmos and Code",             isbn="9781234567890", category=technology, total_copies=2, published_year=2020, authors=[sagan, martin]),     # multiple authors
        ]
        db.add_all(books)
        db.commit()

        # Unpack books by index for loan creation
        (b1984, b_animal, b_hp1, b_hp2, b_dune, b_foundation,
         b_agatha1, b_agatha2, b_hawking, b_cosmos, b_pale,
         b_sapiens, b_homo, b_grand, b_art, b_guns, b_silk,
         b_clean, b_tipping, b_outliers, b_pragmatic, b_cosmoscode) = books

        # ── Members (10+) ─────────────────────────────────────────
        members = [
            Member(full_name="Alice Johnson",   email="alice@example.com",   join_date=date(2022, 1, 10), is_active=True),
            Member(full_name="Bob Smith",        email="bob@example.com",     join_date=date(2022, 3, 15), is_active=True),
            Member(full_name="Carol White",      email="carol@example.com",   join_date=date(2022, 5, 20), is_active=True),
            Member(full_name="David Brown",      email="david@example.com",   join_date=date(2022, 7, 8),  is_active=True),
            Member(full_name="Eva Martinez",     email="eva@example.com",     join_date=date(2023, 1, 3),  is_active=True),
            Member(full_name="Frank Lee",        email="frank@example.com",   join_date=date(2023, 3, 22), is_active=True),
            Member(full_name="Grace Kim",        email="grace@example.com",   join_date=date(2023, 6, 11), is_active=True),
            Member(full_name="Henry Davis",      email="henry@example.com",   join_date=date(2023, 9, 5),  is_active=True),
            Member(full_name="Isla Thompson",    email="isla@example.com",    join_date=date(2024, 1, 18), is_active=True),
            Member(full_name="Jack Wilson",      email="jack@example.com",    join_date=date(2024, 4, 2),  is_active=False),  # inactive member
            Member(full_name="Karen Adams",      email="karen@example.com",   join_date=date(2024, 6, 14), is_active=True),
            Member(full_name="Liam Turner",      email="liam@example.com",    join_date=date(2024, 8, 30), is_active=True),
        ]
        db.add_all(members)
        db.commit()

        alice, bob, carol, david, eva, frank, grace, henry, isla, jack, karen, liam = members

        today = date.today()

        # ── Loans (30+) ───────────────────────────────────────────
        loans = [
            # Returned loans (return_date is set)
            Loan(member=alice,  book=b1984,       loan_date=today-timedelta(60), due_date=today-timedelta(46), return_date=today-timedelta(50)),
            Loan(member=alice,  book=b_hp1,       loan_date=today-timedelta(55), due_date=today-timedelta(41), return_date=today-timedelta(45)),
            Loan(member=bob,    book=b_sapiens,   loan_date=today-timedelta(50), due_date=today-timedelta(36), return_date=today-timedelta(40)),
            Loan(member=bob,    book=b_clean,     loan_date=today-timedelta(45), due_date=today-timedelta(31), return_date=today-timedelta(35)),
            Loan(member=carol,  book=b_cosmos,    loan_date=today-timedelta(40), due_date=today-timedelta(26), return_date=today-timedelta(30)),
            Loan(member=carol,  book=b_dune,      loan_date=today-timedelta(35), due_date=today-timedelta(21), return_date=today-timedelta(25)),
            Loan(member=david,  book=b_homo,      loan_date=today-timedelta(30), due_date=today-timedelta(16), return_date=today-timedelta(20)),
            Loan(member=david,  book=b_outliers,  loan_date=today-timedelta(28), due_date=today-timedelta(14), return_date=today-timedelta(18)),
            Loan(member=eva,    book=b_hawking,   loan_date=today-timedelta(25), due_date=today-timedelta(11), return_date=today-timedelta(15)),
            Loan(member=eva,    book=b_agatha1,   loan_date=today-timedelta(22), due_date=today-timedelta(8),  return_date=today-timedelta(12)),
            Loan(member=frank,  book=b_animal,    loan_date=today-timedelta(20), due_date=today-timedelta(6),  return_date=today-timedelta(10)),
            Loan(member=frank,  book=b_foundation,loan_date=today-timedelta(18), due_date=today-timedelta(4),  return_date=today-timedelta(8)),
            Loan(member=grace,  book=b_tipping,   loan_date=today-timedelta(15), due_date=today-timedelta(1),  return_date=today-timedelta(5)),
            Loan(member=henry,  book=b_pale,      loan_date=today-timedelta(12), due_date=today+timedelta(2),  return_date=today-timedelta(3)),

            # Active loans (return_date is NULL, due_date in the future)
            Loan(member=alice,  book=b_hp2,       loan_date=today-timedelta(10), due_date=today+timedelta(4),  return_date=None),
            Loan(member=bob,    book=b_pragmatic, loan_date=today-timedelta(8),  due_date=today+timedelta(6),  return_date=None),
            Loan(member=carol,  book=b_grand,     loan_date=today-timedelta(7),  due_date=today+timedelta(7),  return_date=None),
            Loan(member=david,  book=b_art,       loan_date=today-timedelta(6),  due_date=today+timedelta(8),  return_date=None),
            Loan(member=eva,    book=b_agatha2,   loan_date=today-timedelta(5),  due_date=today+timedelta(9),  return_date=None),
            Loan(member=grace,  book=b_guns,      loan_date=today-timedelta(4),  due_date=today+timedelta(10), return_date=None),
            Loan(member=henry,  book=b_silk,      loan_date=today-timedelta(3),  due_date=today+timedelta(11), return_date=None),
            Loan(member=isla,   book=b1984,       loan_date=today-timedelta(2),  due_date=today+timedelta(12), return_date=None),
            Loan(member=karen,  book=b_sapiens,   loan_date=today-timedelta(1),  due_date=today+timedelta(13), return_date=None),
            Loan(member=liam,   book=b_clean,     loan_date=today,               due_date=today+timedelta(14), return_date=None),

            # Overdue loans (return_date is NULL, due_date in the past)
            Loan(member=bob,    book=b_cosmoscode, loan_date=today-timedelta(40), due_date=today-timedelta(26), return_date=None),
            Loan(member=carol,  book=b_hp1,        loan_date=today-timedelta(35), due_date=today-timedelta(21), return_date=None),
            Loan(member=frank,  book=b_hawking,    loan_date=today-timedelta(30), due_date=today-timedelta(16), return_date=None),
            Loan(member=grace,  book=b_dune,       loan_date=today-timedelta(25), due_date=today-timedelta(11), return_date=None),
            Loan(member=henry,  book=b_outliers,   loan_date=today-timedelta(20), due_date=today-timedelta(6),  return_date=None),
            Loan(member=isla,   book=b_homo,       loan_date=today-timedelta(15), due_date=today-timedelta(1),  return_date=None),
            Loan(member=liam,   book=b_cosmos,     loan_date=today-timedelta(10), due_date=today-timedelta(3),  return_date=None),
        ]
        db.add_all(loans)
        db.commit()

        print("Seeded successfully:")
        print(f"  {len(books)} books across 4 categories")
        print(f"  10 authors")
        print(f"  {len(members)} members")
        print(f"  {len(loans)} loans (14 returned, 10 active, 7 overdue)")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
