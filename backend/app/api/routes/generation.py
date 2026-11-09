import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import GeneratedDocument, UserSetting, Template
from app.schemas.schemas import DocumentGenerateRequest, GeneratedDocumentResponse
from app.services.generation.generator_service import create_document

router = APIRouter(prefix="/generation", tags=["Document Generation"])

def _format_gen_doc(g: GeneratedDocument) -> GeneratedDocumentResponse:
    return GeneratedDocumentResponse(
        id=g.id,
        title=g.title,
        filename=g.filename,
        format=g.format,
        category=g.category,
        file_size=g.file_size,
        created_at=g.created_at,
        download_url=f"/api/v1/generation/download/{g.id}"
    )

@router.get("/list", response_model=List[GeneratedDocumentResponse])
def list_generated_documents(db: Session = Depends(get_db)):
    """Retrieve all previously generated Word, PDF, and Excel documents."""
    docs = db.query(GeneratedDocument).order_by(GeneratedDocument.created_at.desc()).all()
    return [_format_gen_doc(d) for d in docs]

@router.post("/generate", response_model=GeneratedDocumentResponse, status_code=status.HTTP_201_CREATED)
def generate_document_endpoint(req: DocumentGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate a corporate Word (.docx), PDF, or Excel (.xlsx) document.
    Incorporates company letterhead, formal headings, tables, formulas, and deterministic calculations.
    """
    user_setting = db.query(UserSetting).first()
    company_name = user_setting.company_name if user_setting else "INDUSERV Technologies"
    company_details = user_setting.company_details if user_setting else ""

    content_to_use = req.content or req.user_instructions or "Document généré automatiquement par la plateforme INDUSERV."

    # If template code provided, look up template
    template_id = None
    if req.template_code:
        tpl = db.query(Template).filter(Template.code == req.template_code).first()
        if tpl:
            template_id = tpl.id

    try:
        gen_result = create_document(
            format_type=req.format,
            title=req.title,
            category=req.category,
            content=content_to_use,
            company_name=company_name,
            company_details=company_details,
            calculation_data=req.calculation_data
        )

        gen_doc = GeneratedDocument(
            title=req.title,
            filename=gen_result["filename"],
            file_path=gen_result["file_path"],
            format=gen_result["format"],
            category=req.category,
            file_size=gen_result["file_size"],
            template_id=template_id
        )
        db.add(gen_doc)
        db.commit()
        db.refresh(gen_doc)

        return _format_gen_doc(gen_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération du document: {str(e)}")

@router.get("/download/{doc_id}")
def download_generated_document(doc_id: int, db: Session = Depends(get_db)):
    """Download a generated document file."""
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == doc_id).first()
    if not doc or not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Fichier généré introuvable")

    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type=media_types.get(doc.format, "application/octet-stream")
    )

