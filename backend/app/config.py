import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

    APP_NAME: str = "AgroHisob CFO"
    APP_VERSION: str = "1.0.0-mvp"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    
    # API Settings
    API_V1_PREFIX: str = "/api"
    
    # Database Settings
    # PostgreSQL by default; falls back to sqlite for local testing if Postgres is not active
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://agrohisob:agrohisob_secret@localhost:5432/agrohisob_db"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./agrohisob_local.db"
    
    # CORS Origins (parsed dynamically from env or default local dev ports)
    CORS_ORIGINS_RAW: Union[str, List[str]] = os.getenv(
        "ALLOWED_ORIGINS",
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,https://agrohisob-cfo.vercel.app"
        )
    )
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS_RAW, list):
            return self.CORS_ORIGINS_RAW
        if isinstance(self.CORS_ORIGINS_RAW, str):
            return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"]
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "agrohisob-dev-secret-key-uzbekistan-2026-agrifintech")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://qyawvaoswvpzruhyehqn.supabase.co")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "sb_publishable_lVCYYvwvdaFljmQhIJdScw_MrU1BaPt")
    SUPABASE_JWT_SECRET: Union[str, None] = os.getenv("SUPABASE_JWT_SECRET", None)
    
    # Financial Engine Defaults (Uzbekistan benchmarks)
    DEFAULT_CBU_POLICY_RATE: float = 0.14  # 14.0% CBU rate as of Nov 2026
    COMMERCIAL_LOAN_RATE: float = 0.235    # 23.5% average commercial agro loan rate
    PREFERENTIAL_AGRO_RATE: float = 0.14   # 10-14% state preferential fund rate (PQ-47/Agrofin)
    MIN_ACCEPTABLE_DSCR: float = 1.25      # Standard banking debt service coverage threshold

    # AI & LLM Settings
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def validate_production_security(self) -> None:
        """Logs warnings or raises issues if unsafe defaults are used in production."""
        if self.ENVIRONMENT.lower() == "production":
            if "dev-secret-key" in self.SECRET_KEY:
                logger.warning("SECURITY ALERT: Using default dev SECRET_KEY in production! Please set SECRET_KEY in environment.")
            if self.DEBUG:
                logger.warning("SECURITY ALERT: DEBUG is enabled in production environment!")

settings = Settings()
settings.validate_production_security()
