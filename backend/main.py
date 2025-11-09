"""
FastAPI Application Entry Point - Main server configuration and initialization.
Configures the FastAPI application with CORS middleware and routes, providing
the REST API interface for the carousel generation pipeline.

Main Functions:
    1. root() - Returns API discovery information and endpoint documentation
    2. Main execution block - Launches uvicorn server with hot reload

Connections:
    - Routes: Includes app.router.routes for all API endpoints
    - Configuration: Uses environment variables for port and host settings
    - Started by: run_backend.sh or direct Python execution
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.router.routes import router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Carousel Pipeline API",
    description="Agentic pipeline for automated carousel content generation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Carousel Pipeline API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

