from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routers import auth, resumes, application_kits
from app.routers import analysis
from app.core.config import settings
from app.core.database import test_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

# CORS configuration
cors_origins = []
if settings.BACKEND_CORS_ORIGINS:
    cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]
else:
    # sensible defaults for local development
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(application_kits.router, prefix="/application-kits", tags=["application_kits"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])

# Startup event to test MongoDB connection
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    connection_ok = await test_connection()
    if not connection_ok:
        logger.warning("MongoDB connection failed - some features may not work")
    else:
        logger.info("All systems ready!")

# Healthcheck
@app.get("/health", tags=["health"])
async def health_check():
    connection_ok = await test_connection()
    return {
        "status": "ok",
        "mongodb": "connected" if connection_ok else "disconnected"
    }

# Debug endpoint to catch any unhandled requests
@app.get("/", tags=["root"])
async def root():
    return {"message": "IPA Backend API is running", "auth_endpoint": "/auth/google"}
