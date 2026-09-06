from config import get_settings

from .client import get_openai_client

settings = get_settings()

async def embed_texts(texts : list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = get_openai_client()
    response = await client.embeddings.create(
        model = settings.azure_openai_embedding_deployment,
        input=texts,
    )
    return [item.embedding for item in response.data]    