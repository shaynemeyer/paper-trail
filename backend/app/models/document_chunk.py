from datetime import datetime, UTC
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field

from app.config import EMBEDDING_DIM


# Database table model (table=True). One row per chunk of a document's
# extracted markdown text -- this is what chat retrieval searches, not
# Document.embedding (which only embeds the document's name).
class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"
    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    chunk_index: int
    content: str
    embedding: list[float] | None = Field(
        default=None, sa_column=Column(Vector(EMBEDDING_DIM))
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
