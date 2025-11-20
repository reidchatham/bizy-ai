"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

# Import routes
from api.routes import docs, auth_proxy, tasks, goals, briefings
# from api.routes import analytics, dashboard

app = FastAPI(
    title="Bizy AI API",
    description="AI-Powered Business Planning & Execution Agent",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url=None,  # Disabled - use Swagger UI or Simple Docs instead
    openapi_url="/api/openapi.json"
)

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Allow CDN scripts for Swagger UI to work
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com"
    return response


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "bizy-ai-api",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bizy AI API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "simple_docs": "/api/simple-docs",
        "health": "/health"
    }


# Include routers
app.include_router(docs.router, prefix="/api", tags=["documentation"])
app.include_router(auth_proxy.router, prefix="/api/auth", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(briefings.router, prefix="/api/briefings", tags=["briefings"])
# app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
# app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
