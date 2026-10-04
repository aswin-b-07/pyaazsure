import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.api.lots import router as lots_router
from backend.api.images import router as images_router
from backend.api.reports import router as reports_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PyaazSure API",
    description="Smart Onion Quality Assessment & Grading System API (SIH 2026 Prototype)",
    version="1.0.0"
)

# Enable CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Route (defined before static mount)
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "system": "PyaazSure - Smart Onion Quality Assessment & Grading System",
        "version": "1.0.0",
        "mock_inference_enabled": True
    }

# Include API routers
app.include_router(lots_router)
app.include_router(images_router)
app.include_router(reports_router)

from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# Mount uploaded media files
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Mount frontend web application at root
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

