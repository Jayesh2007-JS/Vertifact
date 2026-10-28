"""Configuration settings for Vertifact Backend."""

import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_env_file():
    """Lightweight standard-library .env file loader."""
    candidate_paths = [
        WORKSPACE_DIR / ".env",
        BASE_DIR / ".env",
        Path.cwd() / ".env"
    ]
    for env_path in candidate_paths:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass


load_env_file()


class Settings(BaseModel):
    APP_NAME: str = "Vertifact"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md"}
    
    # LLM Settings
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)
    OPENAI_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Verification & chunking settings
    CHUNK_SIZE_WORDS: int = 180
    CHUNK_OVERLAP_WORDS: int = 40
    MAX_RETRIEVED_PASSAGES_PER_CLAIM: int = 3
    RELEVANCE_THRESHOLD: float = 0.15
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ]


settings = Settings()

