from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router

app = FastAPI(
    title="CIVIC-EYE API",
    description="AI-Powered Geospatial Change Intelligence Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "CIVIC-EYE API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
