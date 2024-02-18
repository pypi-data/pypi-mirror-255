from enum import Enum
from typing import Any

from pydantic import BaseModel

from notdiamond.exceptions import UnsupportedLLMProvider

class ProviderEnum(Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"

class ProviderModel(BaseModel):
    openai: ProviderEnum = ProviderEnum.openai
    anthropic: ProviderEnum = ProviderEnum.anthropic
    google: ProviderEnum = ProviderEnum.google

possible_models = {
    "gpt-3.5-turbo",
    "gpt-4",
    "claude-2",
    "gemini-pro"
}

class NDLLMProvider:
    def __init__(self, provider: ProviderModel, model: str, api_key: str) -> None:
        if(model not in possible_models):
            raise UnsupportedLLMProvider(f"Given LLM model {model} is not in the list of supported models.")

        self.provider = provider
        self.model = model
        self.api_key = api_key
    
    def prepare_for_request(self):
        return {
            "provider": self.provider.value,
            "model": self.model
        }
