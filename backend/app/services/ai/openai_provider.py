import json
import time
import httpx
from typing import Dict, Any, List, Optional
from app.services.ai.base import AIProvider
from app.core.logging import logger

class OpenAICompatibleProvider(AIProvider):
    """
    Generic provider for any OpenAI-compatible API endpoint
    (OpenAI, Groq, Mistral, DeepSeek, Together AI, vLLM, etc.).
    """

    def __init__(self, base_url: str = "https://api.openai.com/v1", api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        super().__init__(base_url, api_key, model_name or "gpt-4o-mini")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> str:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                return f"[ERREUR API {resp.status_code}] {resp.text}"
        except Exception as e:
            logger.error(f"OpenAICompatible error: {e}")
            return f"[ERREUR DE CONNEXION: {str(e)}]"

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        instruction = f"\n\nIMPORTANT: Répondez UNIQUEMENT en JSON valide respectant ce schéma :\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
        raw_text = await self.generate_text(prompt + instruction, system_prompt, temperature=0.1)
        try:
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.startswith("```"): cleaned = cleaned[3:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {"raw_content": raw_text}

    async def test_connection(self) -> Dict[str, Any]:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                latency_ms = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                    return {
                        "success": True,
                        "message": f"Connexion établie avec succès ({latency_ms} ms).",
                        "latency_ms": latency_ms,
                        "models": models[:20]
                    }
                return {
                    "success": False,
                    "message": f"Erreur de statut {resp.status_code}: {resp.text[:120]}",
                    "latency_ms": latency_ms,
                    "models": []
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Échec de connexion: {str(e)}",
                "latency_ms": None,
                "models": []
            }

    async def list_models(self) -> List[str]:
        test_res = await self.test_connection()
        if test_res["success"] and test_res.get("models"):
            return test_res["models"]
        return [self.model_name]

