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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(brands_router, prefix=settings.api_prefix)

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Voice API - Brand Voice Management Service",
            "version": settings.app_version,
            "docs": "/docs",
        }

    return app
