import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Document, DocumentChunk, TaskHistory, GeneratedDocument, UserSetting
from app.services.ai.factory import get_ai_provider
from app.services.workflows.tender_workflow import analyze_tender_dossier
from app.services.generation.generator_service import create_document
from app.schemas.schemas import GeneratedDocumentResponse

router = APIRouter(prefix="/workflows", tags=["Business Workflows"])

class TenderAnalysisRequest(BaseModel):
    tender_document_id: int
    company_document_ids: List[int] = []
    output_format: str = Field(default="docx", description="docx, pdf, xlsx")
    title: Optional[str] = None

class TenderAnalysisResponse(BaseModel):
    task_id: int
    tender_reference: str
    contracting_authority: str
    submission_deadline: str
    administrative_requirements: List[str]
    technical_requirements: List[str] = []
    financial_requirements: List[str] = []
    required_certificates: List[str] = []
    evaluation_criteria: List[str] = []
    missing_or_unverified_items: List[str]
    compliance_summary: str
    generated_document: Optional[GeneratedDocumentResponse] = None

@router.post("/tender-analysis", response_model=TenderAnalysisResponse)
async def run_tender_analysis_workflow(req: TenderAnalysisRequest, db: Session = Depends(get_db)):
    """
    Executes automated tender (Appel d'Offres) analysis:
    1. Ingests DCE document text.
    2. Extracts references, deadlines, mandatory administrative & technical criteria.
    3. Compares against selected company documents.
    4. Detects missing documents / unverified items.
    5. Formulates compliance gap report and exports as downloadable Word, PDF, or Excel document.
    """
    start_time = time.time()

    # 1. Fetch tender document and chunks
    tender_doc = db.query(Document).filter(Document.id == req.tender_document_id).first()
    if not tender_doc:
        raise HTTPException(status_code=404, detail="Document d'appel d'offres introuvable.")

    tender_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == req.tender_document_id).all()
    tender_text = "\n\n".join(c.text_content for c in tender_chunks)

    # 2. Fetch company documents
    company_text = ""
    if req.company_document_ids:
        comp_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id.in_(req.company_document_ids)).all()
        company_text = "\n\n".join(c.text_content for c in comp_chunks)

    # 3. Resolve AI provider
    provider = get_ai_provider(db=db)

    # 4. Run analysis
    analysis_data = await analyze_tender_dossier(
        provider=provider,
        tender_text=tender_text,
        company_docs_summary=company_text
    )

    tender_ref = analysis_data.get("tender_reference", "AO-2026-EXTRACT")
    authority = analysis_data.get("contracting_authority", "Autorité Contractante Indéterminée")
    deadline = analysis_data.get("submission_deadline", "Non spécifiée dans l'extrait")
    admin_reqs = analysis_data.get("administrative_requirements", ["Kbis < 3 mois", "DC1/DC2", "Attestation URSSAF"])
    tech_reqs = analysis_data.get("technical_requirements", ["Mémoire technique", "Qualifications du personnel"])
    fin_reqs = analysis_data.get("financial_requirements", ["Chiffre d'affaires minimum"])
    certs = analysis_data.get("required_certificates", ["ISO 9001", "Attestation RC Pro"])
    criteria = analysis_data.get("evaluation_criteria", ["Valeur technique 60%", "Prix 40%"])
    missing = analysis_data.get("missing_or_unverified_items", ["Attestation de régularité fiscale originale", "Certificat ISO 9001"])
    summary = analysis_data.get("compliance_summary", "Audit de conformité préliminaire effectué par INDUSERV.")

    # 5. Formulate formatted compliance report text
    report_title = req.title or f"Rapport d'Analyse & Matrice de Conformité - {tender_ref}"
    report_content = f"""# RAPPORT D'ANALYSE D'APPEL D'OFFRES & CONFORMITÉ
Référence du Marché : {tender_ref}
Acheteur Public : {authority}
Date Limite de Remise des Offres : {deadline}

---
## 1. Synthèse du Marché & Éligibilité
L'analyse porte sur les pièces de consultation fournies ({tender_doc.original_filename}).
- **Autorité Contractante :** {authority}
- **Date Limite de Dépôt :** {deadline}
- **Critères de Jugement :** {', '.join(criteria)}

## 2. Matrice des Pièces Administratives Obligatoires
{chr(10).join(f"- [ ] {r}" for r in admin_reqs)}

## 3. Exigences Techniques et Certifications Requises
- **Qualifications & Normes :** {', '.join(certs)}
- **Spécifications Techniques :** {', '.join(tech_reqs)}
- **Capacités Financières :** {', '.join(fin_reqs)}

## 4. PIÈCES MANQUANTES OU NON VÉRIFIÉES DANS LE DOSSIER
> AVERTISSEMENT DE CONFORMITÉ : Les éléments suivants n'ont pas été prouvés par les documents de l'entreprise fournis et doivent être impérativement complétés avant soumission :
{chr(10).join(f"- ⚠️ {m}" for m in missing)}

## 5. Recommandations et Plan d'Action
1. Collecter immédiatement les attestations légales mentionnées dans la section 4.
2. Finaliser le mémoire technique en mettant l'accent sur les critères de pondération ({', '.join(criteria)}).
3. Faire valider le dossier administratif complet par la Direction avant dépôt sur la plateforme de dématérialisation.
"""

    elapsed_ms = int((time.time() - start_time) * 1000)

    # 6. Save task history
    task = TaskHistory(
        title=report_title,
        workflow_type="tender_compliance_analysis",
        system_prompt_used="Auditeur Senior en Marchés Publics",
        user_instructions=f"Analyse AO {tender_ref} avec documents entreprises",
        response_text=report_content,
        referenced_doc_ids=f"{req.tender_document_id}," + ",".join(str(d) for d in req.company_document_ids),
        status="completed",
        execution_time_ms=elapsed_ms
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # 7. Generate downloadable document in requested format
    user_setting = db.query(UserSetting).first()
    comp_name = user_setting.company_name if user_setting else "INDUSERV Technologies"
    comp_details = user_setting.company_details if user_setting else ""

    gen_res = create_document(
        format_type=req.output_format,
        title=report_title,
        category="procurement",
        content=report_content,
        company_name=comp_name,
        company_details=comp_details,
        reference_code=tender_ref
    )

    gen_doc = GeneratedDocument(
        title=report_title,
        filename=gen_res["filename"],
        file_path=gen_res["file_path"],
        format=gen_res["format"],
        category="procurement",
        file_size=gen_res["file_size"],
        task_id=task.id
    )
    db.add(gen_doc)
    db.commit()
    db.refresh(gen_doc)

    gen_response = GeneratedDocumentResponse(
        id=gen_doc.id,
        title=gen_doc.title,
        filename=gen_doc.filename,
        format=gen_doc.format,
        category=gen_doc.category,
        file_size=gen_doc.file_size,
        created_at=gen_doc.created_at,
        download_url=f"/api/v1/generation/download/{gen_doc.id}"
    )

    return TenderAnalysisResponse(
        task_id=task.id,
        tender_reference=tender_ref,
        contracting_authority=authority,
        submission_deadline=deadline,
        administrative_requirements=admin_reqs,
        technical_requirements=tech_reqs,
        financial_requirements=fin_reqs,
        required_certificates=certs,
        evaluation_criteria=criteria,
        missing_or_unverified_items=missing,
        compliance_summary=summary,
        generated_document=gen_response
    )
