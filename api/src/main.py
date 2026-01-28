from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.presentation.dependencies import get_container
from src.presentation.routes import health_router, items_router, queue_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    container = get_container()

    # Startup
    await container.startup()

    yield

    # Shutdown
    await container.shutdown()


def create_app() -> FastAPI:
    """Application factory for creating the FastAPI app."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="FastAPI CRUD service with clean architecture",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router)
    app.include_router(items_router)
    app.include_router(queue_router)

    return app


# Create the application instance
app = create_app()
