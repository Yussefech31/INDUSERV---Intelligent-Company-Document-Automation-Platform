from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import AIProviderSetting
from app.schemas.schemas import (
    AIProviderSettingResponse,
    AIProviderSettingUpdate,
    AIProviderTestRequest,
    AIProviderTestResponse
)
from app.services.ai.free_provider import FreeAPIProvider
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.openai_provider import OpenAICompatibleProvider

router = APIRouter(prefix="/providers", tags=["AI Providers"])

def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "********"
    return f"{key[:4]}...{key[-4:]}"

def _format_provider(p: AIProviderSetting) -> AIProviderSettingResponse:
    return AIProviderSettingResponse(
        id=p.id,
        provider_type=p.provider_type,
        name=p.name,
        base_url=p.base_url,
        model_name=p.model_name,
        is_active=p.is_active,
        temperature=p.temperature,
        max_tokens=p.max_tokens,
        has_api_key=bool(p.api_key),
        masked_key=_mask_key(p.api_key or ""),
        created_at=p.created_at,
        updated_at=p.updated_at
    )

@router.get("/", response_model=List[AIProviderSettingResponse])
def list_providers(db: Session = Depends(get_db)):
    """List all configured AI providers with masked API keys."""
    providers = db.query(AIProviderSetting).order_by(AIProviderSetting.id).all()
    return [_format_provider(p) for p in providers]

@router.put("/{provider_id}", response_model=AIProviderSettingResponse)
def update_provider(provider_id: int, data: AIProviderSettingUpdate, db: Session = Depends(get_db)):
    """Update AI provider settings (Base URL, API Key, Model, Temperature)."""
    p = db.query(AIProviderSetting).filter(AIProviderSetting.id == provider_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Provider setting not found")

    update_dict = data.model_dump(exclude_unset=True)
    if update_dict.get("is_active") is True:
        db.query(AIProviderSetting).filter(AIProviderSetting.id != provider_id).update({AIProviderSetting.is_active: False})

    for key, value in update_dict.items():
        if key == "api_key" and (value is None or value == ""):
            continue
        setattr(p, key, value)

    db.commit()
    db.refresh(p)
    return _format_provider(p)

@router.post("/{provider_id}/activate", response_model=AIProviderSettingResponse)
def activate_provider(provider_id: int, db: Session = Depends(get_db)):
    """Set an AI provider as the primary active provider for all workflows."""
    p = db.query(AIProviderSetting).filter(AIProviderSetting.id == provider_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Provider setting not found")

    db.query(AIProviderSetting).update({AIProviderSetting.is_active: False})
    p.is_active = True
    db.commit()
    db.refresh(p)
    return _format_provider(p)

@router.post("/test", response_model=AIProviderTestResponse)
async def test_provider_connection(req: AIProviderTestRequest, db: Session = Depends(get_db)):
    """Test connection, measure latency, and discover models for an AI provider configuration."""
    api_key = req.api_key
    # If key wasn't passed in test request, retrieve from existing DB record if available
    if not api_key:
        existing = db.query(AIProviderSetting).filter(
            AIProviderSetting.provider_type == req.provider_type
        ).first()
        if existing and existing.api_key:
            api_key = existing.api_key

    if req.provider_type == "ollama":
        provider = OllamaProvider(base_url=req.base_url, model_name=req.model_name)
    elif req.provider_type == "openai_compatible":
        provider = OpenAICompatibleProvider(base_url=req.base_url, api_key=api_key, model_name=req.model_name)
    else:
        provider = FreeAPIProvider(base_url=req.base_url, api_key=api_key, model_name=req.model_name)

    result = await provider.test_connection()
    return AIProviderTestResponse(
        success=result["success"],
        message=result["message"],
        latency_ms=result.get("latency_ms"),
        models_available=result.get("models", [])
    )

