# app/routes/root.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Paper Trail API"}
