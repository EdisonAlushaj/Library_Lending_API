from fastapi import FastAPI

app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
    description="Backend API for a small library lending system.",
)

@app.get("/api/v1/health")
def health_chack():
    return {"status": "ok", "library": "open"}