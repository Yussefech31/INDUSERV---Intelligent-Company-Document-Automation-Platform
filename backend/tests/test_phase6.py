import pytest
from app.services.ai.ollama_provider import OllamaProvider
from app.services.ai.factory import get_ai_provider
from app.models.entities import AIProviderSetting

@pytest.mark.asyncio
async def test_ollama_provider_offline_handling():
    ollama = OllamaProvider(base_url="http://localhost:11434", model_name="llama3.2:latest")
    test_conn = await ollama.test_connection()
    assert "success" in test_conn
    assert "message" in test_conn

    response = await ollama.generate_text("Bonjour assistant.")
    assert len(response) > 0
    assert "OLLAMA" in response or len(response) > 10

def test_ai_provider_factory_switching(setup_database):
    db = setup_database

    db.query(AIProviderSetting).update({AIProviderSetting.is_active: False})
    ollama_db = db.query(AIProviderSetting).filter(AIProviderSetting.provider_type == "ollama").first()
    assert ollama_db is not None
    ollama_db.is_active = True
    db.commit()

    provider = get_ai_provider(db=db)
    assert isinstance(provider, OllamaProvider)
    assert provider.model_name == "llama3.2:latest"
