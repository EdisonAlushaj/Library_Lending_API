from fastapi import FastAPI
from app.routers import books, members, authors, categories

app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
    description="Backend API for a small library lending system.",
)

app.include_router(books.router, prefix="/api/v1")
app.include_router(members.router, prefix="/api/v1")
app.include_router(authors.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")

@app.get("/api/v1/health")
def health_chack():
    return {"status": "ok", "library": "open"}