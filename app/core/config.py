# File: app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Model API"
    PROJECT_VERSION: str = "1.0.0"
    SUPPORTED_MODELS: list = [
        "gpt2",
        "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "meta-llama/Llama-3.2-3B-Instruct",
        "meta-llama/Llama-3.2-11B-Vision-Instruct",
    ]
    ALLOWED_ORIGINS: list = ["*"]

settings = Settings()

