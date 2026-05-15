import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()


def verify_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("API_KEY")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail={"error": "Invalid API key"})