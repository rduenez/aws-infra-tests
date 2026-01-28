from fastapi import APIRouter, Depends

from src.presentation.dependencies import Container, get_container

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(container: Container = Depends(get_container)):
    """
    Health check endpoint for load balancer and container orchestration.

    Returns the application status and version.
    """
    return {
        "status": "healthy",
        "app_name": container.settings.app_name,
        "version": container.settings.app_version,
    }


@router.get("/ready")
async def readiness_check(container: Container = Depends(get_container)):
    """
    Readiness check endpoint.

    Verifies that all dependencies (database, etc.) are available.
    """
    try:
        # Check database connection via ORM
        from sqlalchemy import text
        async with container.db_session.session_factory() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
    }
