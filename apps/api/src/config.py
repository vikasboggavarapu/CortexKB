from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Knowledge Base API"
    environment: str = "development"
    debug: bool = False

    database_url: str
    chroma_host: str = "chromadb"
    chroma_port: int = 8000

    jwt_secret_key: str = "mykey"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
     # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2023-05-15"
    azure_openai_embedding_deployment: str = ""
    azure_openai_chat_deployment: str = ""
    azure_openai_max_tokens: int = 1024

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64
    
    chroma_data_path: str = "./chroma_data"



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()