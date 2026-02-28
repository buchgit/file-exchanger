from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-me-in-production-use-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    STORAGE_PATH: Path = Path(__file__).parent / "storage"

    DATABASE_URL: str = "sqlite:///./file_exchanger.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
