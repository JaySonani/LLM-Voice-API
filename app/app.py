"""FastAPI application factory."""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configs.settings import settings

from app.routes import brands_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(brands_router, prefix=settings.api_prefix)
    # app.include_router(evaluation_router, prefix=settings.api_prefix)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Voice API - Brand Voice Management Service",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health"
        }

    return app
