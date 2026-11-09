import pytest
from app.services.ai.free_provider import FreeAPIProvider

def test_health_check(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "counts" in data

def test_list_and_create_system_prompts(client):
    # List initial seeded prompts
    res = client.get("/api/v1/prompts/")
    assert res.status_code == 200
    prompts = res.json()
    assert len(prompts) >= 3

    # Create new prompt
    new_prompt = {
        "name": "Audit Conformité Juridique",
        "description": "Validation des clauses contractuelles sensibles",
        "content": "Vous êtes un auditeur juridique rigoureux...",
        "category": "legal",
        "is_default": False
    }
    create_res = client.post("/api/v1/prompts/", json=new_prompt)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["name"] == new_prompt["name"]
    assert created["category"] == "legal"

def test_set_default_prompt(client):
    res = client.get("/api/v1/prompts/")
    prompts = res.json()
    target_id = prompts[1]["id"]

    res_set = client.post(f"/api/v1/prompts/{target_id}/set-default")
    assert res_set.status_code == 200
    data = res_set.json()
    assert data["is_default"] is True

def test_providers_endpoints(client):
    res = client.get("/api/v1/providers/")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) >= 3

    test_req = {
        "provider_type": "free_api",
        "base_url": "https://openrouter.ai/api/v1",
        "model_name": "meta-llama/llama-3.3-70b-instruct:free"
    }
    test_res = client.post("/api/v1/providers/test", json=test_req)
    assert test_res.status_code == 200
    data = test_res.json()
    assert "success" in data

@pytest.mark.asyncio
async def test_free_provider_fallback_generation():
    provider = FreeAPIProvider()
    response = await provider.generate_text("Rédiger une lettre administrative.")
    assert len(response) > 50
    assert "INDUSERV" in response or "MODE ASSISTANT" in response

def test_workspace_chat_endpoint(client):
    payload = {
        "message": "Analyser le document de marché public pour INDUSERV.",
        "include_calculations": True
    }
    res = client.post("/api/v1/workspace/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert data["task_id"] > 0
    assert data["execution_time_ms"] >= 0
