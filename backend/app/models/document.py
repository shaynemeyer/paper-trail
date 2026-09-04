from datetime import datetime, UTC
from enum import Enum
from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Column, DateTime, String
from sqlmodel import SQLModel, Field

from app.config import EMBEDDING_DIM


class DocumentStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"


# Database table model (table=True)
class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(max_length=500)
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
    description: str = Field(max_length=500)
    doctype: str = "pdf"
    document_source: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: DocumentStatus = DocumentStatus.draft


# Partial update validation
class DocumentUpdate(SQLModel):
    name: str | None = None
    description: str | None = Field(default=None, max_length=500)
    doctype: str | None = None
    document_source: str | None = None
    tags: list[str] | None = None
    status: DocumentStatus | None = None


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
