from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.entities import Document, GeneratedDocument, TaskHistory, CalculationAudit, AIProviderSetting
from app.schemas.schemas import DashboardStatsResponse, TaskHistoryResponse, GeneratedDocumentResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Retrieve aggregate statistics, document breakdown, and recent activity for the dashboard."""
    total_docs = db.query(Document).count()
    total_gen = db.query(GeneratedDocument).count()
    total_tasks = db.query(TaskHistory).count()
    total_calc = db.query(CalculationAudit).count()

    active_provider = db.query(AIProviderSetting).filter(AIProviderSetting.is_active == True).first()
    provider_name = active_provider.name if active_provider else "Aucun (Mode Fallback)"
    model_name = active_provider.model_name if active_provider else "N/A"

    # Category distribution of generated documents and templates
    gen_cats = db.query(GeneratedDocument.category, func.count(GeneratedDocument.id)).group_by(GeneratedDocument.category).all()
    cat_dist = {cat or "general": count for cat, count in gen_cats}
    if not cat_dist:
        cat_dist = {
            "administrative": 0,
            "procurement": 0,
            "financial": 0,
            "commercial": 0,
            "hr": 0,
            "operations": 0
        }

    recent_tasks_db = db.query(TaskHistory).order_by(TaskHistory.created_at.desc()).limit(5).all()
    recent_tasks = [TaskHistoryResponse.model_validate(t) for t in recent_tasks_db]

    recent_gen_db = db.query(GeneratedDocument).order_by(GeneratedDocument.created_at.desc()).limit(5).all()
    recent_gen = [
        GeneratedDocumentResponse(
            id=g.id,
            title=g.title,
            filename=g.filename,
            format=g.format,
            category=g.category,
            file_size=g.file_size,
            created_at=g.created_at,
            download_url=f"/api/v1/generation/download/{g.id}"
        )
        for g in recent_gen_db
    ]

    return DashboardStatsResponse(
        total_documents=total_docs,
        total_generated=total_gen,
        total_tasks=total_tasks,
        total_calculations=total_calc,
        active_provider=provider_name,
        active_model=model_name,
        category_distribution=cat_dist,
        recent_tasks=recent_tasks,
        recent_generated=recent_gen
    )

