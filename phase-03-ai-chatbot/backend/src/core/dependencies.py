"""
Dependency Injection for Repository Pattern (T099)

This module provides FastAPI dependencies for injecting the appropriate
task repository implementation based on Dapr availability.
"""

import httpx
from typing import Optional

from src.core.repository_interface import TaskRepository
from src.services.dapr_task_repository import DaprTaskRepository
from src.services.fallback_task_repository import FallbackTaskRepository


# Global repository instance (singleton pattern)
_repository: Optional[TaskRepository] = None


async def check_dapr_availability() -> bool:
    """
    Check if Dapr sidecar is available.

    Returns:
        True if Dapr is available, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:3500/v1.0/healthz")
            return response.status_code == 204
    except Exception:
        return False


async def get_repository() -> TaskRepository:
    """
    Get the appropriate task repository implementation.

    Returns Dapr repository if available, otherwise falls back to SQL repository.
    This is a FastAPI dependency that can be injected into route handlers.

    Returns:
        TaskRepository implementation (Dapr or Fallback)
    """
    global _repository

    # Return cached repository if available
    if _repository is not None:
        return _repository

    # Check Dapr availability and initialize appropriate repository
    dapr_available = await check_dapr_availability()

    if dapr_available:
        print("[OK] Dapr sidecar detected - using DaprTaskRepository")
        _repository = DaprTaskRepository()
    else:
        print("[FALLBACK] Dapr sidecar not available - using FallbackTaskRepository")
        _repository = FallbackTaskRepository()

    return _repository


def reset_repository() -> None:
    """
    Reset the repository singleton (useful for testing).
    """
    global _repository
    _repository = None
