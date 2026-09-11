import json
import httpx

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.llm import LLMAnswer

class LLMServiceError(Exception):
    """Raised when the LLM service cannot produce a valid response."""

class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> LLMAnswer:
        # Call the Model
        try:
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

        except httpx.HTTPError as exc:
            raise LLMServiceError(
                "The LLM Service is unavailable"
            ) from exc

        # Data Extraction to JSON
        try:
            data = response.json()
            raw_response = data["response"]
            parsed_response = json.loads(raw_response)

        except (ValueError, KeyError) as exc:
            raise LLMServiceError(
                "The LLM returned invalid response"
            ) from exc

        # Return the data and also try to validate it
        try:
            return LLMAnswer.model_validate(parsed_response)

        except ValidationError as exc:
            raise LLMServiceError(
                "The LLM returned invalid structured response"
            ) from exc

ollama_client = OllamaClient()