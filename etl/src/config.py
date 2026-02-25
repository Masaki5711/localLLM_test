from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    llm_service_url: str = "http://localhost:8002"
    database_url: str = "postgresql+asyncpg://graphrag:changeme_postgres@localhost:5432/graphrag"
    redis_url: str = "redis://localhost:6379"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "changeme_minio"
    minio_bucket: str = "documents"
    cors_allowed_origin: str = "http://localhost:3000"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
