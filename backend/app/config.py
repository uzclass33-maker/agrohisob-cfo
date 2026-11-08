import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

    APP_NAME: str = "AgroHisob CFO"
    APP_VERSION: str = "1.0.0-mvp"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api"
    
    # Database Settings
    # PostgreSQL by default; falls back to sqlite for local testing if Postgres is not active
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://agrohisob:agrohisob_secret@localhost:5432/agrohisob_db"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./agrohisob_local.db"
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "agrohisob-dev-secret-key-uzbekistan-2026-agrifintech")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Financial Engine Defaults (Uzbekistan benchmarks)
    DEFAULT_CBU_POLICY_RATE: float = 0.14  # 14.0% CBU rate as of Nov 2026
    COMMERCIAL_LOAN_RATE: float = 0.235    # 23.5% average commercial agro loan rate
    PREFERENTIAL_AGRO_RATE: float = 0.14   # 10-14% state preferential fund rate (PQ-47/Agrofin)
    MIN_ACCEPTABLE_DSCR: float = 1.25      # Standard banking debt service coverage threshold

settings = Settings()
