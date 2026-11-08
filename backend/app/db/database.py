import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    """Attempts to connect to PostgreSQL. Falls back to SQLite if PostgreSQL is unavailable."""
    try:
        # Test PostgreSQL connection with a short timeout
        pg_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 2}
        )
        with pg_engine.connect() as conn:
            logger.info("Successfully connected to primary PostgreSQL database.")
            return pg_engine
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({settings.DATABASE_URL}). "
            f"Falling back to local SQLite engine ({settings.SQLITE_FALLBACK_URL}). Reason: {e}"
        )
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
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)
