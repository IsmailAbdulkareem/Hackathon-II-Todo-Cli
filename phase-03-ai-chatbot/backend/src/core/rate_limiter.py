"""Rate limiting middleware for API endpoints."""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store: user_id -> (request_count, window_start_time)
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

    def check_rate_limit(self, user_id: str) -> None:
        """
        Check if user has exceeded rate limit.

        Args:
            user_id: User identifier

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        current_time = time.time()
        count, window_start = self.requests[user_id]

        # Check if we're still in the same time window
        if current_time - window_start < self.window_seconds:
            if count >= self.max_requests:
                logger.warning(f"Rate limit exceeded for user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds."
                )
            # Increment count in current window
            self.requests[user_id] = (count + 1, window_start)
        else:
            # Start new window
            self.requests[user_id] = (1, current_time)

        logger.debug(f"Rate limit check passed for user_id={user_id} - {self.requests[user_id][0]}/{self.max_requests} requests")

    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limit for a specific user.

        Args:
            user_id: User identifier
        """
        if user_id in self.requests:
            del self.requests[user_id]
            logger.info(f"Rate limit reset for user_id={user_id}")


# Global rate limiter instance
# 10 requests per minute per user for chat endpoint
chat_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
