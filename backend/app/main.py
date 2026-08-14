import structlog

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging


configure_logging()

settings = get_settings()

logger = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    logger.info(
        "application_started",
        environment=settings.environment,
    )


@app.get("/health")
async def health():
    logger.info("health_check")

    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }