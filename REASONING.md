# REASONING.md

## 1. Why did you choose your database

The projects uses SQLite for development and PostgreSQL for Docker (production)

**SQLite** is easy to use, it does not need server to intall, what it needs it a library.db file. This is perfect for development and running tests locally, the tests use it in memory (`sqlite://`)

**PostgreSQL** is used in Docker because it's a production level database, it handles concurrent connections properly. SQLite has it more harder when there multply requests at the same time, PostgreSQL handles that without issues.

There is no problem switching between them, what is needed is only to change the `DATABASE_URL` environment variable, there is no need to change the code.

---

## 2. Why you modelled the M:N relationship the way you did

A book can have many authors and also the other way the author can have many books, this is many-to-many relationship.
I implemented an plain SQLAlchemy `Table` that is called `book_authors` with two foreign key columns (`book_id`, `author_id`). Then i connect it to both `Book` and `Author` models by adding a `relationship(secondary=book_authors)`.

I used an plain table instead of a model class because there are no extra data that is needed to be added, this table is used only to link book and authors.

---

## 3. How you implemented search to avoid N+1 queries

The N+1 problem is that when i fetch 20 books and for each book that is being fetched there is a seperate query to get the authors and category, this is not preferred.
The fix to this bug is using Eager Loading with `joinedload`. This works by when i query books, i tell SQLAlchemy to also load the authors and category in the same query, not one by one:

```python
query.options(joinedload(Book.authors), joinedload(Book.category))
```

There is another N+1 risk in the search feature, when filtering the `author_id`, if there were a JOIN in the `book_authors` and in the `joinedload`, the two JOINs can interfere and inflate result, so the fix was to use a subquery for the author filter instead of a JOIN:

```python
Book.id.in_(
    db.query(book_authors.c.book_id).filter(book_authors.c.author_id == author_id)
)
```

And for the total count, I used `func.count(Book.id.distinct())` to prevent counting duplicate rows that are caused by the outerjoin.

---

## 4. Why DELETE on a member with active loans returns 409

This is simple, if i delete a member with an active loans, then the loans in the database would have an `member_id` that does not exist anymore, even if the database would allow it then the data would be corrupted.

An simple example is that if a book is still loan to that member then the library has no records who has the book.

**409 Conflict** is the right HTTP status because the resource exist but the current state of the system conflicts with the delete operation, this is not a client mistake (400) or a missing data (404), this is a state of conflict.

The same logic is also implemented to the `DELETE /books/{id}`, you can't delete a book that is currently borrowed.

---

## 5. How did you structure the test suite

I tested:

- The core loan lifecycle: borrow → return → double-return. This is one of the core logic that should work.
- Error cases: inactive member, no copies available, double-return. These should be tested for the app to be ready.
- Book search: title filter, `available_only`.

Every test gets a fresh in-memory SQLite database. No test depends on another test's state.

---

## 6. Scope Choices

I finished everything in the assessment: full CRUD for 4 resources, loan feature, book search with filters, both reports endpoints, API key auth, Alembic migration, seed data, tests, README, Docker.

I kept simple some features:

- **Auth:** I didn't implement JWT or OAuth2. I used a static API key from enviroment variable.
- **SQLite in dev:** I didn't complicate this one, used the SQLite when developing and PostgreSQL only in Docker where it matters.

---

## 7. External Resources

From external resources i used Claude Code, it was used in a weay as an interative tutor, prompts focused on understanding design decisions and debugging specific error.

Some of the prompts like understanding what this project is about:

**Planning the architecture:**

> "I have to do this assessment, I want you to help me make a plan on how to implement this."

This prompt produced the phased implementation plan (database → CRUD → loans → search → reports → seed → tests → Docker).

**Debugging the many-to-many seed issue:**

> "It showed UNIQUE constraint failed: book_authors."

This revealed that `db.query(Book).delete()` bypasses cascade rules. The fix was to explicitly delete from `book_authors` first using `db.execute(book_authors.delete())` before deleting books.

**Guiding the learning approach:**

> "I would like you to show me how it is implemented and me to write the code — this is an assessment for me to learn."

This shaped the entire collaboration method: Claude explained the code and the reasoning, the student typed and implemented it themselves.


(I ask Claude Code to format this file)
