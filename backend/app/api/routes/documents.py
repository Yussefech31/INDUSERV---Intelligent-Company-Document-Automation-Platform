import os
import shutil
import uuid
import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Document, DocumentChunk
from app.schemas.schemas import DocumentResponse, DocumentDetailResponse, DocumentChunkResponse
from app.core.config import settings
from app.services.documents.extractor import extract_and_chunk_document

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """Retrieve all uploaded documents ordered by creation date."""
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_detail(document_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed document metadata and all indexed text chunks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")

    metadata = {}
    try:
        metadata = json.loads(doc.metadata_json or "{}")
    except Exception:
        pass

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index).all()
    chunk_responses = [DocumentChunkResponse.model_validate(c) for c in chunks]

    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        mime_type=doc.mime_type,
        page_count=doc.page_count,
        chunk_count=doc.chunk_count,
        status=doc.status,
        error_message=doc.error_message,
        is_scanned_likely=doc.is_scanned_likely,
        created_at=doc.created_at,
        metadata=metadata,
        chunks=chunk_responses
    )

@router.post("/upload", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """
    Ingest multiple company documents (PDF, DOCX, XLSX, CSV, TXT).
    Validates file sizes, stores them locally, extracts content, and indexes chunks.
    """
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    results: List[Document] = []

    for file in files:
        original_name = file.filename or "unnamed_document"
        suffix = Path(original_name).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non pris en charge: {suffix}. Formats acceptés: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Unique safe storage filename
        safe_filename = f"{uuid.uuid4().hex[:12]}_{Path(original_name).name}"
        destination_path = settings.UPLOAD_DIR / safe_filename

        # Write uploaded file stream
        file_size = 0
        with open(destination_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    buffer.close()
                    if destination_path.exists():
                        destination_path.unlink()
                    raise HTTPException(status_code=400, detail=f"Fichier trop volumineux (max 50 Mo): {original_name}")
                buffer.write(chunk)

        # Extract and chunk document
        extraction_res = extract_and_chunk_document(str(destination_path), original_name)

        doc = Document(
            filename=safe_filename,
            original_filename=original_name,
            file_path=str(destination_path),
            file_type=extraction_res["file_type"],
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            page_count=extraction_res.get("page_count", 1),
            chunk_count=extraction_res.get("chunk_count", 0),
            status="processed" if extraction_res["success"] else "error",
            error_message=extraction_res.get("error_message"),
            metadata_json=extraction_res.get("metadata_json", "{}"),
            is_scanned_likely=extraction_res.get("is_scanned_likely", False)
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Insert chunks
        for c in extraction_res.get("chunks", []):
            chunk_record = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                text_content=c["text_content"],
                page_number=c.get("page_number"),
                sheet_name=c.get("sheet_name"),
                section_title=c.get("section_title"),
                token_count=c.get("token_count", 0)
            )
            db.add(chunk_record)

        db.commit()
        results.append(doc)

    return results

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document, its local file, and its indexed chunks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")

    # Remove file from storage
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return None

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download the original source document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable sur le disque")

    return FileResponse(
        path=doc.file_path,
        filename=doc.original_filename,
        media_type=doc.mime_type
    )

