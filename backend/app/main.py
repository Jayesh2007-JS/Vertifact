"""Main FastAPI application entry point for Vertifact."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import router
from backend.app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An Evidence-Grounded AI Hallucination Detection Platform.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration allowing local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits localhost:3000, 127.0.0.1:3000, etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback exception handler ensuring structured error responses."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
