from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Template
from app.schemas.schemas import TemplateResponse

router = APIRouter(prefix="/templates", tags=["Templates & Catalog"])

@router.get("/", response_model=List[TemplateResponse])
def list_templates(category: Optional[str] = None, db: Session = Depends(get_db)):
    """List document templates from the enterprise catalog."""
    query = db.query(Template)
    if category and category.lower() != "all":
        query = query.filter(Template.category == category.lower())
    return query.order_by(Template.category, Template.name).all()

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific template."""
    tpl = db.query(Template).filter(Template.id == template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Modèle introuvable")
    return tpl

@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    name: str,
    category: str,
    code: str,
    description: str,
    default_prompt: str,
    supported_formats: str = "docx,pdf",
    db: Session = Depends(get_db)
):
    """Create a new custom document template in the catalog."""
    existing = db.query(Template).filter(Template.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Un modèle avec le code '{code}' existe déjà.")

    tpl = Template(
        name=name,
        category=category,
        code=code,
        description=description,
        default_prompt=default_prompt,
        supported_formats=supported_formats,
        is_custom=True
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return tpl

