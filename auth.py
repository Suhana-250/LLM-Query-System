import os
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization format. Use 'Bearer <token>'"
        )
    token = authorization.split(" ")[1]
    if token != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
