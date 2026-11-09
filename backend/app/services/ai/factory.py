from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.entities import AIProviderSetting
from app.services.ai.base import AIProvider
from app.services.ai.free_provider import FreeAPIProvider
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.openai_provider import OpenAICompatibleProvider

def get_ai_provider(provider_id: Optional[int] = None, db: Optional[Session] = None) -> AIProvider:
    """
    Factory to retrieve an initialized AIProvider instance.
    Checks DB for the requested or active provider; falls back to environment defaults.
    """
    if db:
        query = db.query(AIProviderSetting)
        if provider_id:
            setting = query.filter(AIProviderSetting.id == provider_id).first()
        else:
            setting = query.filter(AIProviderSetting.is_active == True).first()

        if setting:
            if setting.provider_type == "ollama":
                return OllamaProvider(
                    base_url=setting.base_url or settings.OLLAMA_BASE_URL,
                    model_name=setting.model_name or settings.OLLAMA_DEFAULT_MODEL
                )
            elif setting.provider_type == "openai_compatible":
                return OpenAICompatibleProvider(
                    base_url=setting.base_url,
                    api_key=setting.api_key,
                    model_name=setting.model_name
                )
            else:
                return FreeAPIProvider(
                    base_url=setting.base_url or settings.FREE_API_BASE_URL,
                    api_key=setting.api_key or settings.FREE_API_KEY,
                    model_name=setting.model_name or settings.FREE_API_DEFAULT_MODEL
                )

    # Fallback to application settings from environment
    if settings.DEFAULT_AI_PROVIDER == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model_name=settings.OLLAMA_DEFAULT_MODEL
        )
    return FreeAPIProvider(
        base_url=settings.FREE_API_BASE_URL,
        api_key=settings.FREE_API_KEY,
        model_name=settings.FREE_API_DEFAULT_MODEL
    )

