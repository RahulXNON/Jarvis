import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from jarvis.config import settings
from jarvis.core.llm_service import llm_service
from jarvis.core.memory_service import memory_service
from jarvis.core.task_logger import task_logger
from jarvis.api.routes import create_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("jarvis.log")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting JARVIS application...")

    # Record start time
    app.state.start_time = time.time()

    # Initialize services (lazy initialization for memory)
    await llm_service.initialize()
    await task_logger.initialize()

    logger.info("JARVIS application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down JARVIS application...")

    await llm_service.close()
    await memory_service.close()
    await task_logger.close()

    logger.info("JARVIS application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="JARVIS AI Assistant",
        description="A personal AI assistant with memory and task logging",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create API routes
    create_routes(app)

    return app


# Create the FastAPI application instance
app = create_app()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}