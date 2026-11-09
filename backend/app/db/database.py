import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def normalize_database_url(raw_url: str) -> str:
    """
    Normalizes PostgreSQL/Supabase URLs for SQLAlchemy 2.0+ compatibility with psycopg2.
    Replaces 'postgres://' or 'postgresql://' with 'postgresql+psycopg2://'.
    """
    if not raw_url:
        return settings.SQLITE_FALLBACK_URL
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+"):
        return raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return raw_url

def get_engine():
    """
    Attempts to connect to PostgreSQL (including Supabase or Railway).
    Falls back gracefully to SQLite if PostgreSQL is unavailable.
    """
    normalized_pg_url = normalize_database_url(settings.DATABASE_URL)
    
    # Try PostgreSQL connection if URL indicates PostgreSQL
    if "postgresql" in normalized_pg_url:
        try:
            pg_engine = create_engine(
                normalized_pg_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=300,
                connect_args={"connect_timeout": 3}
            )
            with pg_engine.connect() as conn:
                logger.info(f"Successfully connected to primary PostgreSQL database at {normalized_pg_url.split('@')[-1] if '@' in normalized_pg_url else 'target'}.")
                return pg_engine
        except Exception as e:
            logger.warning(
                f"Could not connect to PostgreSQL ({normalized_pg_url}). "
                f"Falling back to local SQLite engine ({settings.SQLITE_FALLBACK_URL}). Reason: {e}"
            )
            
    # SQLite fallback engine
    return create_engine(
        settings.SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False}
    )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes all registered models and tables in the database."""
    import app.models.core  # Ensure all SQLAlchemy models are registered
    Base.metadata.create_all(bind=engine)
