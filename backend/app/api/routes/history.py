from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import TaskHistory, GeneratedDocument
from app.schemas.schemas import TaskHistoryResponse, GeneratedDocumentResponse

router = APIRouter(prefix="/history", tags=["Task History"])

@router.get("/", response_model=List[TaskHistoryResponse])
def get_task_history(db: Session = Depends(get_db)):
    """Retrieve chronologically ordered history of all AI and document generation tasks."""
    tasks = db.query(TaskHistory).order_by(TaskHistory.created_at.desc()).limit(100).all()
    results = []
    for t in tasks:
        gen_docs = [
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
            for g in t.generated_documents
        ]
        results.append(TaskHistoryResponse(
            id=t.id,
            title=t.title,
            workflow_type=t.workflow_type,
            user_instructions=t.user_instructions,
            response_text=t.response_text,
            referenced_doc_ids=t.referenced_doc_ids or "",
            status=t.status,
            execution_time_ms=t.execution_time_ms,
            created_at=t.created_at,
            generated_documents=gen_docs
        ))
    return results

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_history(task_id: int, db: Session = Depends(get_db)):
    """Delete a task history record."""
    t = db.query(TaskHistory).filter(TaskHistory.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tâche introuvable")

    db.delete(t)
    db.commit()
    return None

