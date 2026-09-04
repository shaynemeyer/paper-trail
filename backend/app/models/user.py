from datetime import datetime, UTC
from enum import Enum
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


# Database table model (table=True)
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str
    role: UserRole = Field(default=UserRole.user)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    # Bumped explicitly by the patch route, not a DB-level trigger
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# Request validation (create)
class UserCreate(SQLModel):
    email: str
    name: str
    role: UserRole = UserRole.user


# Partial update validation
class UserUpdate(SQLModel):
    email: str | None = None
    name: str | None = None
    role: UserRole | None = None


# Response model
class UserRead(SQLModel):
    id: int
    email: str
    name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
