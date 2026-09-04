# app/routes/documents.py
from datetime import datetime, UTC
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.chunking import chunk_text
from app.config import MARKDOWN_DIR, RAW_PDF_DIR
from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentRead
from app.models.document_chunk import DocumentChunk
from app.database import get_session
from app.auth.permissions import require_user, require_admin
from app.embeddings import embed_text
from app.logger import get_logger
from app.pdf import pdf_to_markdown

router = APIRouter()
logger = get_logger(__name__)


def document_to_read(document: Document) -> DocumentRead:
    return DocumentRead(
        **document.model_dump(exclude={"embedding", "raw_path", "markdown_path"}),
        raw_url=f"/api/documents/{document.id}/raw" if document.raw_path else None,
        markdown_url=f"/api/documents/{document.id}/markdown"
        if document.markdown_path
        else None,
    )


@router.get("/documents", response_model=list[DocumentRead])
async def get_documents(
    session: AsyncSession = Depends(get_session), user: dict = Depends(require_user)
):
    result = await session.execute(select(Document))
    return [document_to_read(d) for d in result.scalars().all()]


@router.post("/documents", status_code=201, response_model=DocumentRead)
async def create_document(
    document: DocumentCreate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Create a new document.

    Returns:
        201: Document created successfully
        401: Unauthorized
        422: Validation error
    """
    db_document = Document(**document.model_dump())

    session.add(db_document)

    try:
        await session.commit()
        await session.refresh(db_document)

        logger.info(
            "document_created",
            document_id=db_document.id,
            document_name=db_document.name,
            user_id=user.get("sub"),
        )

        return document_to_read(db_document)

    except Exception as e:
        logger.error(
            "document_creation_failed",
            error=str(e),
            document_name=document.name,
            user_id=user.get("sub"),
        )
        raise HTTPException(status_code=500, detail="Failed to create document")


@router.post("/documents/upload", status_code=201, response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(..., max_length=500),
    document_source: str | None = Form(None),
    tags: str = Form(""),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Upload a PDF: save the raw file, extract + chunk + embed its text.

    `tags` is a comma-separated string (multipart forms don't carry native lists).

    Returns:
        201: Document uploaded and processed successfully
        400: Not a PDF
        401: Unauthorized
        422: Validation error
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    db_document = Document(
        name=name,
        description=description,
        document_source=document_source,
        tags=tag_list,
    )
    session.add(db_document)
    await session.commit()
    await session.refresh(db_document)

    raw_path = RAW_PDF_DIR / f"{db_document.id}.pdf"
    raw_path.write_bytes(await file.read())

    markdown_text = pdf_to_markdown(raw_path)
    markdown_path = MARKDOWN_DIR / f"{db_document.id}.md"
    markdown_path.write_text(markdown_text)

    for index, chunk in enumerate(chunk_text(markdown_text)):
        session.add(
            DocumentChunk(
                document_id=db_document.id,
                chunk_index=index,
                content=chunk,
                embedding=await embed_text(chunk),
            )
        )

    db_document.raw_path = str(raw_path)
    db_document.markdown_path = str(markdown_path)
    db_document.status = "pending"
    db_document.updated_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(db_document)

    logger.info(
        "document_uploaded",
        document_id=db_document.id,
        document_name=db_document.name,
        user_id=user.get("sub"),
    )

    return document_to_read(db_document)


@router.get("/documents/{document_id}/raw")
async def get_document_raw(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Serve the raw uploaded PDF."""
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document or not document.raw_path:
        raise HTTPException(status_code=404, detail="Raw file not found")

    return FileResponse(document.raw_path, media_type="application/pdf")


@router.get("/documents/{document_id}/markdown")
async def get_document_markdown(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Serve the processed markdown extracted from the PDF."""
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document or not document.markdown_path:
        raise HTTPException(status_code=404, detail="Markdown file not found")

    return FileResponse(document.markdown_path, media_type="text/markdown")


@router.get("/documents/search", response_model=list[DocumentRead])
async def search_documents(
    q: str,
    limit: int = 5,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Semantic search over embedded documents (nearest by cosine distance)."""
    query_embedding = await embed_text(q)
    result = await session.execute(
        select(Document)
        .where(Document.embedding.is_not(None))
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return [document_to_read(d) for d in result.scalars().all()]


@router.post("/documents/{document_id}/embed", response_model=DocumentRead)
async def embed_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Generate and store the embedding for a document's name via Ollama.

    Returns:
        200: Document embedded successfully
        404: Document not found
        401: Unauthorized
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    db_document = result.scalar_one_or_none()

    if not db_document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    db_document.embedding = await embed_text(db_document.name)
    db_document.updated_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(db_document)

    logger.info(
        "document_embedded", document_id=db_document.id, user_id=user.get("sub")
    )

    return document_to_read(db_document)


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Get a single document by ID.

    Returns:
        200: Document found
        404: Document not found
        401: Unauthorized
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    return document_to_read(document)


@router.put("/documents/{document_id}", response_model=DocumentRead)
async def update_document(
    document_id: int,
    document: DocumentCreate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Fully replace a document (requires all fields).

    Returns:
        200: Document updated successfully
        404: Document not found
        401: Unauthorized
        422: Validation error
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    db_document = result.scalar_one_or_none()

    if not db_document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    db_document.name = document.name
    db_document.description = document.description
    db_document.doctype = document.doctype
    db_document.document_source = document.document_source
    db_document.tags = document.tags
    db_document.status = document.status
    db_document.updated_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(db_document)

    return document_to_read(db_document)


@router.patch("/documents/{document_id}", response_model=DocumentRead)
async def patch_document(
    document_id: int,
    document: DocumentUpdate,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Partially update a document (only updates provided fields).

    Returns:
        200: Document updated successfully
        400: No fields to update
        404: Document not found
        401: Unauthorized
        422: Validation error
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    db_document = result.scalar_one_or_none()

    if not db_document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    update_data = document.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(db_document, field, value)
    db_document.updated_at = datetime.now(UTC)

    await session.commit()
    await session.refresh(db_document)

    return document_to_read(db_document)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_admin),
):
    """Delete a document (admin only).

    Returns:
        204: Document deleted successfully
        404: Document not found
        401: Unauthorized
        403: Forbidden (not admin)
    """
    result = await session.execute(select(Document).where(Document.id == document_id))
    db_document = result.scalar_one_or_none()

    if not db_document:
        raise HTTPException(
            status_code=404, detail=f"Document with id {document_id} not found"
        )

    await session.delete(db_document)
    await session.commit()

    return Response(status_code=204)
