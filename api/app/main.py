"""Main FastAPI application for GPT-5.6 multimodal API"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os

from app.config import Settings
from app.routes import health, analyze, transcribe, chat, documents, risk_analysis
from app.services.openai_service import OpenAIService
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration
settings = Settings()

# Initialize OpenAI service
openai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    global openai_service
    
    # Startup
    logger.info("Starting up GPT-5.6 Multimodal API with Risk Analysis")
    openai_service = OpenAIService(
        api_key=settings.openai_api_key,
        model=settings.model_name
    )
    logger.info(f"Initialized OpenAI service with model: {settings.model_name}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GPT-5.6 Multimodal API")

# Create FastAPI app
app = FastAPI(
    title="GPT-5.6 Multimodal API",
    description="Multimodal AI service integrating OpenAI's GPT-5.6 with Azure - Support for text, audio, images, transaction extraction, and EU risk analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["Transcription"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["Document Extraction"])
app.include_router(risk_analysis.router, prefix="/api/v1", tags=["Risk Analysis"])

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "error": exc.detail,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.debug
    )
