from fastapi import FastAPI
from app.core.config import settings
from app.core.logger import logger
from app.routers import mv_integration

app = FastAPI(
    title="MV Integra API",
    description="API for integrating with MV System (Oracle SQL DB)",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up MV Integra API...")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down MV Integra API...")

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "MV Integra API"}

app.include_router(mv_integration.router)
