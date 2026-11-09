from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncIterator

class AIProvider(ABC):
    """
    Abstract Base Class for AI providers in INDUSERV.
    Guarantees provider independence: switching between Free API, local Ollama,
    or OpenAI-compatible APIs requires zero modifications to business workflows.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, model_name: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> str:
        """Generate plain or markdown text completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON conforming to a target schema."""
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Verify provider availability, latency, and list available models.
        Returns: {"success": bool, "message": str, "latency_ms": int, "models": List[str]}
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """Retrieve available model identifiers for this provider."""
        pass

