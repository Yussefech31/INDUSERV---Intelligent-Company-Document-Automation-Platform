from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import SystemPrompt
from app.schemas.schemas import SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse

router = APIRouter(prefix="/prompts", tags=["System Prompts"])

@router.get("/", response_model=List[SystemPromptResponse])
def list_system_prompts(db: Session = Depends(get_db)):
    """List all system prompt profiles."""
    return db.query(SystemPrompt).order_by(SystemPrompt.is_default.desc(), SystemPrompt.name).all()

@router.get("/{prompt_id}", response_model=SystemPromptResponse)
def get_system_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Get a specific system prompt by ID."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    return prompt

@router.post("/", response_model=SystemPromptResponse, status_code=status.HTTP_201_CREATED)
def create_system_prompt(data: SystemPromptCreate, db: Session = Depends(get_db)):
    """Create a new customizable system prompt profile."""
    if data.is_default:
        # Clear default flag on others
        db.query(SystemPrompt).update({SystemPrompt.is_default: False})

    new_prompt = SystemPrompt(**data.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

@router.put("/{prompt_id}", response_model=SystemPromptResponse)
def update_system_prompt(prompt_id: int, data: SystemPromptUpdate, db: Session = Depends(get_db)):
    """Update an existing system prompt."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")

    update_dict = data.model_dump(exclude_unset=True)
    if update_dict.get("is_default") is True:
        db.query(SystemPrompt).filter(SystemPrompt.id != prompt_id).update({SystemPrompt.is_default: False})

    for key, value in update_dict.items():
        setattr(prompt, key, value)

    db.commit()
    db.refresh(prompt)
    return prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Delete a system prompt."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    if prompt.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default system prompt. Set another default first.")

    db.delete(prompt)
    db.commit()
    return None

@router.post("/{prompt_id}/set-default", response_model=SystemPromptResponse)
def set_default_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Set a prompt profile as the active system default."""
    prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")

    db.query(SystemPrompt).update({SystemPrompt.is_default: False})
    prompt.is_default = True
    db.commit()
    db.refresh(prompt)
    return prompt

