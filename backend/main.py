"""
FastAPI Application Entry Point - Scale66 MVP Backend

Configures the FastAPI application with:
- CORS middleware
- API v1 routes (auth, brand_kit, campaigns, content, posts, social, payment)
- Exception handlers
- Supabase integration

Architecture:
- API Layer: FastAPI routers in app/api/v1/
- Agents: AI pipeline in app/agents/
- CRUD: Database operations in app/crud/
- Services: External integrations in app/services/
"""

import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import API routers
from app.api.v1 import auth, brand_kit, campaigns, content, posts, social, payment
from app.core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scale66 API",
    description="AI-powered carousel content generation platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routers
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(brand_kit.router, prefix="/api/v1", tags=["brand_kit"])
app.include_router(campaigns.router, prefix="/api/v1", tags=["campaigns"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(posts.router, prefix="/api/v1", tags=["posts"])
app.include_router(social.router, prefix="/api/v1", tags=["social"])
app.include_router(payment.router, prefix="/api/v1", tags=["payment"])


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """API root endpoint with service information."""
    return {
        "name": "Scale66 API",
        "version": "2.0.0",
        "description": "AI-powered carousel content generation",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "brand_kit": "/api/v1/brand-kit",
            "campaigns": "/api/v1/campaigns",
            "content": "/api/v1/content",
            "posts": "/api/v1/posts",
            "social": "/api/v1/social",
            "payment": "/api/v1/payment"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "scale66-backend",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

