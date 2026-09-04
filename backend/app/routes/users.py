# app/routes/users.py
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.user import User, UserCreate, UserUpdate, UserRead
from app.database import get_session
from app.auth.permissions import require_admin
from app.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/users", response_model=list[UserRead])
async def get_users(
    session: AsyncSession = Depends(get_session), user: dict = Depends(require_admin)
):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.post("/users", status_code=201, response_model=UserRead)
async def create_user(
    new_user: UserCreate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_admin),
):
    """Create a new user.

    Returns:
        201: User created successfully
        401: Unauthorized
        403: Forbidden (not admin)
        422: Validation error
    """
    db_user = User(**new_user.model_dump())

    session.add(db_user)

    try:
        await session.commit()
        await session.refresh(db_user)

        logger.info(
            "user_created",
            created_user_id=db_user.id,
            created_user_email=db_user.email,
            user_id=user.get("sub"),
        )

        return db_user

    except Exception as e:
        logger.error(
            "user_creation_failed",
            error=str(e),
            email=new_user.email,
            user_id=user.get("sub"),
        )
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/users/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_admin),
):
    """Get a single user by ID.

    Returns:
        200: User found
        404: User not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    return db_user


@router.patch("/users/{user_id}", response_model=UserRead)
async def patch_user(
    user_id: int,
    update: UserUpdate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_admin),
):
    """Partially update a user (only updates provided fields).

    Returns:
        200: User updated successfully
        400: No fields to update
        404: User not found
        401: Unauthorized
        403: Forbidden (not admin)
        422: Validation error
    """
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    update_data = update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(db_user, field, value)
    db_user.updated_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(db_user)

    logger.info("user_updated", updated_user_id=db_user.id, user_id=user.get("sub"))

    return db_user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_admin),
):
    """Delete a user (admin only).

    Returns:
        204: User deleted successfully
        404: User not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    await session.delete(db_user)
    await session.commit()

    logger.info("user_deleted", deleted_user_id=user_id, user_id=user.get("sub"))

    return Response(status_code=204)
