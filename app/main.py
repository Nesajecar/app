from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.database import engine
from app.db import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dog Rescue API",
    description="Sistem za prijavu izgubljenih i nađenih pasa sa potvrdom spašavanja",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded images
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Dog Rescue API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
