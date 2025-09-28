"""Voice API application entry point."""

import logging
import uvicorn

from app.app import create_app
from app.configs.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Start the FastAPI server
    # Database initialization is handled by the FastAPI lifespan event
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )