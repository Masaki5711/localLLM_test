from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "qwen2.5:7b"
    ollama_host: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
