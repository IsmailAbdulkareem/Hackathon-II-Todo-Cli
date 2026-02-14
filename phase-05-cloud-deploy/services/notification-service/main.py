"""
Notification Service - FastAPI application.

Microservice for sending task reminder notifications via email.
Subscribes to Kafka 'reminders' topic via Dapr Pub/Sub.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.config import settings
from src.subscriber import get_subscriber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Dapr App ID: {settings.DAPR_APP_ID}")
    logger.info(f"Dapr App Port: {settings.DAPR_APP_PORT}")
    logger.info(f"Subscribing to topic: {settings.KAFKA_TOPIC_REMINDERS}")

    yield

    # Shutdown
    logger.info("Shutting down notification service")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    Root endpoint - health check.

    Returns:
        Service information
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": settings.DAPR_APP_ID
    }


@app.get("/dapr/subscribe", status_code=status.HTTP_200_OK)
async def subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics this service subscribes to.

    Returns:
        List of subscription configurations
    """
    subscriber = get_subscriber()
    subscriptions = subscriber.get_subscription_config()

    logger.info(f"Dapr subscription request received. Returning {len(subscriptions)} subscription(s)")

    return subscriptions


@app.post("/reminders", status_code=status.HTTP_200_OK)
async def handle_reminder_event(request: Request):
    """
    Handle reminder events from Dapr Pub/Sub.

    This endpoint receives ReminderScheduled events from the 'reminders' topic
    and processes them by sending email notifications.

    Args:
        request: FastAPI request containing event data

    Returns:
        Success response or error
    """
    try:
        # Parse event data
        event_data = await request.json()

        logger.info(f"Received reminder event: {event_data.get('event_type', 'unknown')}")

        # Get subscriber and handle event
        subscriber = get_subscriber()
        success = await subscriber.handle_reminder_scheduled(event_data)

        if success:
            return {
                "status": "success",
                "message": "Reminder processed successfully"
            }
        else:
            # Return 200 even on failure to prevent Dapr from retrying
            # (we handle retries internally)
            return {
                "status": "failed",
                "message": "Reminder processing failed after retries"
            }

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}", exc_info=True)

        # Return 200 to prevent Dapr retry (we handle retries internally)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "message": str(e)
            }
        )


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
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if not settings.is_production else None
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.DAPR_APP_PORT,
        reload=not settings.is_production,
        log_level="info"
    )
