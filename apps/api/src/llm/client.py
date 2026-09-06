from functools import lru_cache

from openai import AsyncAzureOpenAI

from config import get_settings

@lru_cache
def get_openai_client() -> AsyncAzureOpenAI:
    settings = get_settings()
    return AsyncAzureOpenAI(
        api_key = settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version
    )