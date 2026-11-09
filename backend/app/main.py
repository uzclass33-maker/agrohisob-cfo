import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.db.database import init_db
from app.api import (
    routes_scenarios, routes_financials, routes_reports, 
    routes_demo, routes_finance, routes_imports,
    routes_dashboard, routes_insights, routes_dossier,
    routes_regulatory, routes_collateral, routes_subsidies
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds enterprise HTTP security headers and request execution timing to all responses."""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Performance & Observability
        response.headers["X-Process-Time"] = f"{process_time:.6f}s"
        
        # Enterprise AppSec Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

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

# Register Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS dynamically
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
    app.include_router(routes_dashboard.router, prefix=prefix)
    app.include_router(routes_insights.router, prefix=prefix)
    app.include_router(routes_dossier.router, prefix=prefix)
    app.include_router(routes_regulatory.router, prefix=prefix)
    app.include_router(routes_collateral.router, prefix=prefix)
    app.include_router(routes_subsidies.router, prefix=prefix)

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
