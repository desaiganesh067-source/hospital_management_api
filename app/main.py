import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ORIGINS
from app.logging_config import setup_logging
from app.routers import users, doctors, patients, appointments


setup_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Hospital Management API",
    description="Backend API for Hospital Management System",
    version="1.0.0"
)


# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Global Exception Handler
# -----------------------------

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )


# -----------------------------
# Root
# -----------------------------

@app.get("/")
def root():
    logger.info("Root endpoint called")

    return {
        "message": "Hospital Management API is running"
    }


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health_check():
    logger.info("Health check called")

    return {
        "status": "healthy"
    }


# -----------------------------
# Routers
# -----------------------------

app.include_router(users.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)