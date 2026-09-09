import json
import httpx

from app.core.config import settings
from app.schemas.llm import LLMAnswer

class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> LLMAnswer:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        data = response.json()
        raw_response = data["response"]
        parsed_response = json.loads(raw_response)

        return LLMAnswer.model_validate(parsed_response)

ollama_client = OllamaClient()