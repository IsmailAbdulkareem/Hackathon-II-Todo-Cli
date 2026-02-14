"""
Recurring Service - FastAPI application.

Microservice responsible for:
- Listening to TaskCompleted events
- Calculating next recurring task occurrences
- Creating next task instances via backend API
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.subscriber import get_subscriber

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    logger.info(f"Dapr HTTP port: {settings.DAPR_HTTP_PORT}")
    logger.info(f"Subscribing to topic: {settings.TASK_EVENTS_TOPIC}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI application
app = FastAPI(
    title="Recurring Service",
    description="Microservice for managing recurring task instances",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns subscription configuration for Dapr to route events.

    Returns:
        List of subscription configurations
    """
    subscriber = get_subscriber()
    subscriptions = subscriber.get_subscription_config()

    logger.info(f"Dapr subscription config requested: {subscriptions}")
    return subscriptions


@app.post("/task-events")
async def handle_task_event(request: Request):
    """
    Handle task events from Dapr Pub/Sub.

    Processes TaskCompleted events to create recurring task instances.

    Args:
        request: FastAPI request with event data

    Returns:
        Success or retry response
    """
    try:
        # Parse event data
        event_data = await request.json()

        logger.info(
            f"Received task event: {event_data.get('event_type')} "
            f"for task {event_data.get('task', {}).get('id')}"
        )

        # Process event
        subscriber = get_subscriber()
        success = await subscriber.handle_task_completed(event_data)

        if success:
            return Response(status_code=status.HTTP_200_OK)
        else:
            # Return 500 to trigger Dapr retry
            logger.warning("Event processing failed, will retry")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error handling task event: {str(e)}", exc_info=True)
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.

    Args:
        request: FastAPI request
        exc: Exception that occurred

    Returns:
        Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower()
    )
