"""Security tests for JWT authentication and authorization."""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from jose import jwt

from main import app
from src.core.config import settings

client = TestClient(app)


def create_valid_token(user_id: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """Create a valid JWT token for testing."""
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")


def create_expired_token(user_id: str) -> str:
    """Create an expired JWT token for testing."""
    expire = datetime.now(timezone.utc) - timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")


def create_invalid_signature_token(user_id: str) -> str:
    """Create a JWT token with invalid signature for testing."""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expire
    }
    # Use wrong secret to create invalid signature
    return jwt.encode(payload, "wrong-secret-key", algorithm="HS256")


class TestAuthenticationScenarios:
    """Test authentication scenarios (401 responses)."""

    def test_missing_authorization_header(self):
        """T055: Test missing Authorization header returns 401."""
        response = client.get("/api/test-user/tasks")

        assert response.status_code == 401
        assert response.json()["detail"] == "Missing authentication token"
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"

    def test_malformed_authorization_header_no_bearer(self):
        """T054: Test malformed Authorization header (no Bearer prefix) returns 401."""
        token = create_valid_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": token}  # Missing "Bearer" prefix
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authorization header format"
        assert "WWW-Authenticate" in response.headers

    def test_malformed_authorization_header_extra_parts(self):
        """T054: Test malformed Authorization header (extra parts) returns 401."""
        token = create_valid_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token} extra"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid authorization header format"

    def test_invalid_jwt_signature(self):
        """T056: Test invalid JWT signature returns 401."""
        token = create_invalid_signature_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"
        assert "WWW-Authenticate" in response.headers

    def test_expired_jwt_token(self):
        """T057: Test expired JWT token returns 401."""
        token = create_expired_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"
        assert "WWW-Authenticate" in response.headers

    def test_jwt_missing_sub_claim(self):
        """T052: Test JWT without sub claim returns 401."""
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "exp": expire
            # Missing "sub" claim
        }
        token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")

        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token claims"

    def test_completely_invalid_token(self):
        """T054: Test completely invalid token format returns 401."""
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": "Bearer not-a-valid-jwt-token"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"


class TestAuthorizationScenarios:
    """Test authorization scenarios (403 responses)."""

    def test_cross_user_access_get_tasks(self):
        """T058: Test cross-user access attempt returns 403."""
        # User A tries to access User B's tasks
        token = create_valid_token("user-a")
        response = client.get(
            "/api/user-b/tasks",  # Trying to access user-b's tasks
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"

    def test_cross_user_access_create_task(self):
        """T058: Test cross-user task creation attempt returns 403."""
        token = create_valid_token("user-a")
        response = client.post(
            "/api/user-b/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test Task", "description": "Test"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"

    def test_cross_user_access_update_task(self):
        """T058: Test cross-user task update attempt returns 403."""
        token = create_valid_token("user-a")
        response = client.put(
            "/api/user-b/tasks/some-task-id",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Updated", "description": "Updated"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"

    def test_cross_user_access_delete_task(self):
        """T058: Test cross-user task deletion attempt returns 403."""
        token = create_valid_token("user-a")
        response = client.delete(
            "/api/user-b/tasks/some-task-id",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"

    def test_cross_user_access_toggle_completion(self):
        """T058: Test cross-user toggle completion attempt returns 403."""
        token = create_valid_token("user-a")
        response = client.patch(
            "/api/user-b/tasks/some-task-id/complete",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"

    def test_cross_user_access_get_single_task(self):
        """T058: Test cross-user single task access attempt returns 403."""
        token = create_valid_token("user-a")
        response = client.get(
            "/api/user-b/tasks/some-task-id",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Access denied: You can only access your own resources"


class TestRouteProtection:
    """Test that all routes require JWT authentication."""

    def test_all_task_routes_require_auth(self):
        """T059: Verify all task routes require JWT authentication."""
        routes_to_test = [
            ("GET", "/api/test-user/tasks"),
            ("POST", "/api/test-user/tasks"),
            ("GET", "/api/test-user/tasks/task-id"),
            ("PUT", "/api/test-user/tasks/task-id"),
            ("DELETE", "/api/test-user/tasks/task-id"),
            ("PATCH", "/api/test-user/tasks/task-id/complete"),
        ]

        for method, path in routes_to_test:
            if method == "GET":
                response = client.get(path)
            elif method == "POST":
                response = client.post(path, json={"title": "Test", "description": "Test"})
            elif method == "PUT":
                response = client.put(path, json={"title": "Test", "description": "Test"})
            elif method == "DELETE":
                response = client.delete(path)
            elif method == "PATCH":
                response = client.patch(path)

            assert response.status_code == 401, f"{method} {path} should require authentication"
            assert "WWW-Authenticate" in response.headers, f"{method} {path} should include WWW-Authenticate header"


class TestValidAuthentication:
    """Test valid authentication scenarios."""

    def test_valid_token_allows_access(self):
        """Test that valid JWT token allows access to own resources."""
        token = create_valid_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should not be 401 or 403 (may be 200 or 500 depending on database state)
        assert response.status_code not in [401, 403]

    def test_jwt_expiration_validation(self):
        """T052: Verify JWT expiration is validated."""
        # Create token that expires in 1 second
        token = create_valid_token("test-user", expires_delta=timedelta(seconds=1))

        # Should work immediately
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code not in [401, 403]

        # Wait for expiration
        import time
        time.sleep(2)

        # Should fail after expiration
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_jwt_signature_validation(self):
        """T053: Verify JWT signature is validated."""
        # Valid token works
        valid_token = create_valid_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code not in [401, 403]

        # Invalid signature fails
        invalid_token = create_invalid_signature_token("test-user")
        response = client.get(
            "/api/test-user/tasks",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
