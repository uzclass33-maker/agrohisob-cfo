from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import init_db
from app.api import routes_scenarios, routes_financials, routes_reports, routes_demo, routes_finance, routes_imports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    init_db()
    yield
    # Shutdown logic if needed

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AgriFinTech B2B SaaS for Uzbekistan - Core Financial Engine & Pre-Underwriting",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers for both /api and /api/v1 for standard backward & versioned compatibility
for prefix in ["/api", "/api/v1"]:
    app.include_router(routes_scenarios.router, prefix=prefix)
    app.include_router(routes_financials.router, prefix=prefix)
    app.include_router(routes_reports.router, prefix=prefix)
    app.include_router(routes_demo.router, prefix=prefix)
    app.include_router(routes_finance.router, prefix=prefix)
    app.include_router(routes_imports.router, prefix=prefix)

@app.get("/")
def root():
    return {
        "product": "AgroHisob CFO",
        "version": settings.APP_VERSION,
        "status": "active",
        "description": "AgriFinTech B2B SaaS Financial Engine for Uzbekistan",
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "agrohisob-backend",
        "version": settings.APP_VERSION,
        "engine": "Python/FastAPI Financial Engine",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

@app.get("/ready")
def readiness_check():
    return {
        "status": "ready",
        "database": "connected",
        "engine_version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }
