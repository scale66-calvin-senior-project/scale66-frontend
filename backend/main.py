"""
═══════════════════════════════════════════════════════════════════════════
                                  MAIN.PY
       FASTAPI APPLICATION ENTRY POINT - CONFIGURES CORS, ROUTERS, 
            AND STATIC FILE SERVING FOR THE MARKETING PIPELINE API
═══════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from routers import image, brands
from pathlib import Path
import uvicorn  # type: ignore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router)
app.include_router(brands.router)

BRANDS_DIR = Path(__file__).parent / "data" / "clients"
app.mount("/brand-assets", StaticFiles(directory=str(BRANDS_DIR)), name="brand-assets")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
