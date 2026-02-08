"""
Dapr Integration Test Configuration (T010)

This module provides pytest fixtures and configuration for Dapr integration tests.
It sets up the necessary Dapr components and provides utilities for testing
Dapr-enabled features like Pub/Sub, State Store, and Jobs API.
"""

import pytest
import asyncio
import httpx
from typing import AsyncGenerator
import os


# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
DAPR_GRPC_PORT = int(os.getenv("DAPR_GRPC_PORT", "50001"))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


@pytest.fixture(scope="session")
def dapr_config():
    """
    Provide Dapr configuration for tests.

    Returns:
        dict: Dapr configuration including ports and endpoints
    """
    return {
        "http_port": DAPR_HTTP_PORT,
        "grpc_port": DAPR_GRPC_PORT,
        "http_endpoint": f"http://localhost:{DAPR_HTTP_PORT}",
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
    }


@pytest.fixture(scope="session")
async def redis_client():
    """
    Provide a Redis client for integration tests.

    Yields:
        Redis client instance
    """
    try:
        import redis.asyncio as redis
        client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Test connection
        await client.ping()

        yield client

        # Cleanup
        await client.close()
    except ImportError:
        pytest.skip("redis package not installed")
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")


@pytest.fixture
async def dapr_http_client(dapr_config) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Provide an HTTP client configured for Dapr sidecar communication.

    Args:
        dapr_config: Dapr configuration fixture

    Yields:
        httpx.AsyncClient: HTTP client for Dapr API calls
    """
    async with httpx.AsyncClient(
        base_url=dapr_config["http_endpoint"],
        timeout=30.0
    ) as client:
        yield client


@pytest.fixture
async def dapr_state_store(dapr_http_client, dapr_config):
    """
    Provide utilities for testing Dapr State Store.

    Args:
        dapr_http_client: HTTP client fixture
        dapr_config: Dapr configuration fixture

    Returns:
        dict: State store utilities
    """
    store_name = "statestore"

    async def save_state(key: str, value: dict):
        """Save state to Dapr state store"""
        url = f"/v1.0/state/{store_name}"
        payload = [{"key": key, "value": value}]
        response = await dapr_http_client.post(url, json=payload)
        response.raise_for_status()

    async def get_state(key: str):
        """Get state from Dapr state store"""
        url = f"/v1.0/state/{store_name}/{key}"
        response = await dapr_http_client.get(url)
        if response.status_code == 204:
            return None
        response.raise_for_status()
        return response.json()

    async def delete_state(key: str):
        """Delete state from Dapr state store"""
        url = f"/v1.0/state/{store_name}/{key}"
        response = await dapr_http_client.delete(url)
        response.raise_for_status()

    return {
        "save": save_state,
        "get": get_state,
        "delete": delete_state,
        "store_name": store_name,
    }


@pytest.fixture
async def dapr_pubsub(dapr_http_client, dapr_config):
    """
    Provide utilities for testing Dapr Pub/Sub.

    Args:
        dapr_http_client: HTTP client fixture
        dapr_config: Dapr configuration fixture

    Returns:
        dict: Pub/Sub utilities
    """
    pubsub_name = "pubsub"

    async def publish(topic: str, data: dict):
        """Publish message to Dapr Pub/Sub topic"""
        url = f"/v1.0/publish/{pubsub_name}/{topic}"
        response = await dapr_http_client.post(url, json=data)
        response.raise_for_status()

    return {
        "publish": publish,
        "pubsub_name": pubsub_name,
    }


@pytest.fixture
async def dapr_jobs(dapr_http_client, dapr_config):
    """
    Provide utilities for testing Dapr Jobs API.

    Args:
        dapr_http_client: HTTP client fixture
        dapr_config: Dapr configuration fixture

    Returns:
        dict: Jobs API utilities
    """

    async def schedule_job(job_name: str, schedule: str, data: dict):
        """Schedule a job using Dapr Jobs API"""
        url = f"/v1.0-alpha1/jobs/{job_name}"
        payload = {
            "schedule": schedule,
            "data": data,
        }
        response = await dapr_http_client.post(url, json=payload)
        response.raise_for_status()

    async def get_job(job_name: str):
        """Get job details"""
        url = f"/v1.0-alpha1/jobs/{job_name}"
        response = await dapr_http_client.get(url)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def delete_job(job_name: str):
        """Delete a scheduled job"""
        url = f"/v1.0-alpha1/jobs/{job_name}"
        response = await dapr_http_client.delete(url)
        response.raise_for_status()

    return {
        "schedule": schedule_job,
        "get": get_job,
        "delete": delete_job,
    }


@pytest.fixture(autouse=True)
async def cleanup_test_data(redis_client, dapr_config):
    """
    Automatically cleanup test data after each test.

    This fixture runs after each test to clean up any test data
    created during the test execution.
    """
    yield

    # Cleanup Redis test keys
    try:
        if redis_client:
            # Delete all keys matching test patterns
            test_patterns = ["test-*", "task-test-*", "recurring-test-*", "reminder-test-*"]
            for pattern in test_patterns:
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
    except Exception as e:
        # Don't fail tests if cleanup fails
        print(f"Warning: Cleanup failed: {e}")


def pytest_configure(config):
    """
    Configure pytest with custom markers for Dapr integration tests.
    """
    config.addinivalue_line(
        "markers", "dapr: mark test as requiring Dapr runtime"
    )
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip Dapr tests if Dapr is not available.
    """
    skip_dapr = pytest.mark.skip(reason="Dapr runtime not available")
    skip_redis = pytest.mark.skip(reason="Redis not available")

    # Check if Dapr is available
    dapr_available = os.getenv("DAPR_AVAILABLE", "false").lower() == "true"
    redis_available = os.getenv("REDIS_AVAILABLE", "true").lower() == "true"

    for item in items:
        if "dapr" in item.keywords and not dapr_available:
            item.add_marker(skip_dapr)
        if "redis" in item.keywords and not redis_available:
            item.add_marker(skip_redis)
