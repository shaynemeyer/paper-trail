# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.auth.permissions import require_user
from app.chat import ask
from app.config import CHAT_TOP_K
from app.database import get_session
from app.embeddings import embed_text
from app.logger import get_logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

router = APIRouter()
logger = get_logger(__name__)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    chunk_ids: list[int]


@router.post("/documents/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: int,
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Answer a question about a document, grounded only in its embedded chunks.

    Returns:
        200: Answered
        404: Document not found or has no embedded chunks yet
        401: Unauthorized
    """
    document = (
        await session.execute(select(Document).where(Document.id == document_id))
    ).scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    query_embedding = await embed_text(body.message)
    chunks = (
        (
            await session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
                .limit(CHAT_TOP_K)
            )
        )
        .scalars()
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=404, detail="This document has no embedded content yet"
        )

    context = "\n\n---\n\n".join(chunk.content for chunk in chunks)
    answer = await ask(body.message, context)

    logger.info(
        "document_chat",
        document_id=document_id,
        chunk_ids=[c.id for c in chunks],
        user_id=user.get("sub"),
    )

    return ChatResponse(answer=answer, chunk_ids=[c.id for c in chunks])
