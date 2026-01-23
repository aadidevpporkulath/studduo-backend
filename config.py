from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API Settings
    app_env: str = "development"
    api_port: int = 8000
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Google Gemini
    google_api_key: str

    # Firebase
    firebase_project_id: str
    firebase_credentials_path: str = "./firebase-credentials.json"

    # Database
    database_url: str = "sqlite+aiosqlite:///./studduoai.db"

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # PDF Processing
    knowledge_dir: str = "./knowledge"
    tesseract_cmd: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    # LLM Settings
    model_name: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 8192

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
