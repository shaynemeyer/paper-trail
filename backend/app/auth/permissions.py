# app/auth/permissions.py
from fastapi import Depends, HTTPException
from app.auth.jwt import get_current_user


async def require_user(user: dict = Depends(get_current_user)):
    """Require any authenticated user."""
    return user


async def require_admin(user: dict = Depends(get_current_user)):
    """Require admin role."""
    role = user.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Admin access required. Current role: {role or 'none'}",
        )
    return user
