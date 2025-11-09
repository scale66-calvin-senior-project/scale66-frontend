import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.router.routes import router


# Overview:
# - Purpose: Configure and launch the FastAPI application for the carousel pipeline.
# Key Components:
# - app: FastAPI instance with CORS enabled and router attached.
# - root endpoint: provides discovery details for clients.


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

