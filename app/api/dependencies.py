from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os

# 🔥 LOAD ENV
load_dotenv()

# 🔥 DEFINE API KEY
API_KEY = os.getenv("API_KEY")


def verify_api_key(
    x_api_key: str = Header(..., alias="x-api-key")
):
    print("Received:", x_api_key)
    print("Expected:", API_KEY)

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server API key not configured"
        )

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )