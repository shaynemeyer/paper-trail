from datetime import datetime, UTC
from enum import Enum
from pgvector.sqlalchemy import Vector
from pydantic import field_validator
from sqlalchemy import ARRAY, Column, DateTime, String, Text
from sqlmodel import SQLModel, Field

from app.config import EMBEDDING_DIM

DESCRIPTION_MAX_WORDS = 500


def validate_description_word_count(value: str | None) -> str | None:
    """Description is capped by word count, not character count, since it's
    free-form prose (e.g. a pasted abstract) rather than a fixed-width field."""
    if value is None:
        return value
    word_count = len(value.split())
    if word_count > DESCRIPTION_MAX_WORDS:
        raise ValueError(
            f"Description must be {DESCRIPTION_MAX_WORDS} words or fewer (got {word_count})"
        )
    return value


class DocumentStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"


# Database table model (table=True)
class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    # Unbounded column -- validated by word count (see DocumentCreate/Update),
    # not a fixed character length.
    description: str = Field(sa_column=Column(Text))
    # Plain str (not an enum) since more doctypes will be added later
    doctype: str = Field(default="pdf", index=True)
    document_source: str | None = Field(default=None)
    tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    # Filesystem paths (see app.config STORAGE_ROOT), populated by the upload route
    raw_path: str | None = Field(default=None)
    markdown_path: str | None = Field(default=None)
    status: DocumentStatus = Field(default=DocumentStatus.draft)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    # Bumped explicitly by the update/patch routes, not a DB-level trigger
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    # Populated by POST /documents/{id}/embed via app.embeddings.embed_text
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(EMBEDDING_DIM))
    )


# Request validation (create)
class DocumentCreate(SQLModel):
    name: str
    description: str
    doctype: str = "pdf"
    document_source: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.draft

    _validate_description = field_validator("description")(
        validate_description_word_count
    )


# Partial update validation
class DocumentUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    doctype: str | None = None
    document_source: str | None = None
    tags: list[str] | None = None
    status: DocumentStatus | None = None

    _validate_description = field_validator("description")(
        validate_description_word_count
    )


# Response model. raw_url/markdown_url point at the file-serving routes, not
# the server's filesystem paths -- built by documents.document_to_read().
class DocumentRead(SQLModel):
    id: int
    name: str
    description: str
    doctype: str
    document_source: str | None
    tags: list[str]
    raw_url: str | None
    markdown_url: str | None
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime
