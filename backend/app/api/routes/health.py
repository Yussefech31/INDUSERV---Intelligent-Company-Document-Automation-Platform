from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.config import settings
from app.models.entities import Document, TaskHistory, GeneratedDocument

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def check_health(db: Session = Depends(get_db)):
    """Health check endpoint returning system status."""
    doc_count = db.query(Document).count()
    task_count = db.query(TaskHistory).count()
    gen_count = db.query(GeneratedDocument).count()

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "connected",
        "counts": {
            "documents": doc_count,
            "tasks": task_count,
            "generated_files": gen_count
        }
    }

