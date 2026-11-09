import json
import time
import httpx
from typing import Dict, Any, List, Optional
from app.services.ai.base import AIProvider
from app.core.logging import logger

class OllamaProvider(AIProvider):
    """
    Provider for local, 100% offline inference using Ollama (http://localhost:11434).
    Guarantees strict privacy with zero external transmission of confidential documents.
    """

    def __init__(self, base_url: str = "http://localhost:11434", api_key: Optional[str] = None, model_name: str = "llama3.2:latest"):
        super().__init__(base_url, api_key=None, model_name=model_name or "llama3.2:latest")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", "")
                else:
                    return f"[ERREUR OLLAMA: Code HTTP {resp.status_code}] {resp.text}"
        except httpx.ConnectError:
            return (
                "[OLLAMA HORS LIGNE] Impossible de joindre le serveur Ollama local sur "
                f"{self.base_url}. Assurez-vous qu'Ollama est bien lancé (`ollama serve`) "
                f"et que le modèle `{self.model_name}` a été téléchargé (`ollama pull {self.model_name}`)."
            )
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"[ERREUR OLLAMA: {str(e)}]"

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        instruction = f"\n\nIMPORTANT: Répondez STRICTEMENT en JSON respectant ce schéma :\n{json.dumps(schema, ensure_ascii=False)}"
        payload = {
            "model": self.model_name,
            "prompt": prompt + instruction,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    text_out = resp.json().get("response", "{}")
                    return json.loads(text_out)
        except Exception as e:
            logger.warning(f"Ollama structured error: {e}")

        # Fallback to general generate
        raw_text = await self.generate_text(prompt + instruction, system_prompt, temperature=0.1)
        try:
            clean = raw_text.strip()
            if clean.startswith("```json"): clean = clean[7:]
            if clean.startswith("```"): clean = clean[3:]
            if clean.endswith("```"): clean = clean[:-3]
            return json.loads(clean.strip())
        except Exception:
            return {"raw_content": raw_text}

    async def test_connection(self) -> Dict[str, Any]:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                latency_ms = int((time.time() - start_time) * 1000)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return {
                        "success": True,
                        "message": f"Ollama local opérationnel ({latency_ms} ms). {len(models)} modèles locaux installés.",
                        "latency_ms": latency_ms,
                        "models": models
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Ollama a répondu avec le statut {resp.status_code}",
                        "latency_ms": latency_ms,
                        "models": []
                    }
        except httpx.ConnectError:
            return {
                "success": False,
                "message": f"Serveur Ollama non détecté sur {self.base_url}. Démarrez Ollama avec 'ollama serve'.",
                "latency_ms": None,
                "models": []
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur de connexion Ollama: {str(e)}",
                "latency_ms": None,
                "models": []
            }

    async def list_models(self) -> List[str]:
        test_res = await self.test_connection()
        if test_res["success"] and test_res.get("models"):
            return test_res["models"]
        return ["llama3.2:latest", "mistral:latest", "qwen2.5:latest"]

