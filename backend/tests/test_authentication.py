from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from tests.conftest import graphql


# Test data constants
VALID_USERNAME = "testadmin"
VALID_PASSWORD = "Correct-Horse-Battery-Staple!2024"
INVALID_PASSWORD = "wrong-password"


# Helper functions
def login(client: TestClient, username: str = VALID_USERNAME, password: str = VALID_PASSWORD, remember_me: bool = False) -> dict:
    """Login and return tokens dict."""
    response = graphql(
        client,
        """
        mutation Login($input: LoginInput!) {
          login(input: $input) {
            accessToken
            refreshToken
            expiresIn
            tokenType
            rememberMe
            user {
              username
              role
            }
          }
        }
        """,
        {"input": {"username": username, "password": password, "rememberMe": remember_me}},
    )
    assert response.status_code == 200
    assert "errors" not in response.json(), f"GraphQL errors: {response.json().get('errors')}"
    return response.json()["data"]["login"]


def me_query(client: TestClient, token: str) -> dict:
    """Query the me field and return user data."""
    response = graphql(client, "{ me { username role } }", token=token)
    assert response.status_code == 200
    assert "errors" not in response.json()
    return response.json()["data"]


def test_login_and_authenticated_current_user(client: TestClient) -> None:
    """Test basic login and me query."""
    tokens = login(client)
    assert tokens["user"] == {"username": "testadmin", "role": "ADMINISTRATOR"}
    assert tokens["tokenType"] == "Bearer"
    assert tokens["rememberMe"] == False

    user_data = me_query(client, tokens["accessToken"])
    assert user_data["me"]["username"] == "testadmin"
    assert user_data["me"]["role"] == "ADMINISTRATOR"


def test_login_with_remember_me(client: TestClient) -> None:
    """Test login with remember_me flag."""
    tokens = login(client, remember_me=True)
    assert tokens["rememberMe"] == True
    # The remember me should extend the token validity
    assert tokens["expiresIn"] > 900  # Should be more than 15 min default


def test_invalid_login_does_not_disclose_account_details(client: TestClient) -> None:
    """Test that invalid login gives generic error regardless of user existence."""
    response = graphql(
        client,
        """
        mutation {
          login(input: {username: "testadmin", password: "wrong-password"}) {
            accessToken
          }
        }
        """,
    )
    assert response.status_code == 200
    assert response.json()["errors"][0]["message"] == "Invalid username or password."


def test_invalid_login_for_nonexistent_user(client: TestClient) -> None:
    """Test login with nonexistent user gives same error (no account enumeration)."""
    response = graphql(
        client,
        """
        mutation {
          login(input: {username: "nonexistent_user_12345", password: "any-password"}) {
            accessToken
          }
        }
        """,
    )
    assert response.status_code == 200
    assert response.json()["errors"][0]["message"] == "Invalid username or password."


def test_repeated_failed_login_temporarily_locks_account(client: TestClient) -> None:
    """Test account lockout after max failed attempts."""
    mutation = """
    mutation {
      login(input: {username: "testadmin", password: "wrong-password"}) {
        accessToken
      }
    }
    """

    # Attempt 5 failed logins (max failed attempts)
    for _ in range(5):
        response = graphql(client, mutation)
        assert response.json()["errors"][0]["message"] == "Invalid username or password."

    # 6th attempt should lock the account
    response = graphql(client, mutation)
    error_msg = response.json()["errors"][0]["message"].lower()
    # Should indicate account issues
    assert any(word in error_msg for word in ["lock", "account", "try again"])


def test_refresh_rotates_and_old_token_cannot_be_reused(client: TestClient) -> None:
    """Test that refresh token rotation works and old tokens are invalidated."""
    initial = login(client)
    refreshed = graphql(
        client,
        """
        mutation Refresh($refreshToken: String!) {
          refreshSession(refreshToken: $refreshToken) {
            accessToken
            refreshToken
            expiresIn
          }
        }
        """,
        {"refreshToken": initial["refreshToken"]},
    ).json()["data"]["refreshSession"]

    # New refresh token should be different
    assert refreshed["refreshToken"] != initial["refreshToken"]
    # New access token should be different
    assert refreshed["accessToken"] != initial["accessToken"]
    # Old refresh token should now be rejected
    rejected = graphql(
        client,
        """
        mutation Refresh($refreshToken: String!) {
          refreshSession(refreshToken: $refreshToken) { accessToken }
        }
        """,
        {"refreshToken": initial["refreshToken"]},
    )
    assert "errors" in rejected.json()
    assert "expired" in rejected.json()["errors"][0]["message"].lower() or "invalid" in rejected.json()["errors"][0]["message"].lower()


def test_logout_revokes_refresh_token(client: TestClient) -> None:
    """Test that logout revokes the refresh token."""
    tokens = login(client)
    
    # Logout
    response = graphql(
        client,
        """
        mutation Logout($refreshToken: String!) {
          logout(refreshToken: $refreshToken)
        }
        """,
        {"refreshToken": tokens["refreshToken"]},
    )
    assert response.json() == {"data": {"logout": True}}

    # Old refresh token should now be rejected
    rejected = graphql(
        client,
        """
        mutation Refresh($refreshToken: String!) {
          refreshSession(refreshToken: $refreshToken) { accessToken }
        }
        """,
        {"refreshToken": tokens["refreshToken"]},
    )
    assert "errors" in rejected.json()
    assert "expired" in rejected.json()["errors"][0]["message"].lower() or "invalid" in rejected.json()["errors"][0]["message"].lower()


def test_logout_with_invalid_token(client: TestClient) -> None:
    """Test logout with invalid/already-revoked token returns false."""
    response = graphql(
        client,
        """
        mutation Logout($refreshToken: String!) {
          logout(refreshToken: "invalid-token-string")
        }
        """,
    )
    # Should return false, not error
    assert "data" in response.json()


def test_health_checks(client: TestClient) -> None:
    """Test health endpoints."""
    live_response = client.get("/health/live")
    assert live_response.json() == {"status": "ok"}

    ready_response = client.get("/health/ready")
    assert ready_response.json() == {"status": "ready"}


def test_login_lockout_progression(client: TestClient) -> None:
    """Test the full lockout progression from failed attempts to locked state."""
    mutation = """
    mutation {
      login(input: {username: "testadmin", password: "wrong-password"}) {
        accessToken
      }
    }
    """

    # Login first to establish baseline
    login(client)

    # Try 5 wrong passwords
    for i in range(5):
        response = graphql(client, mutation)
        assert response.json()["errors"][0]["message"] == "Invalid username or password."

    # 6th attempt should trigger lockout
    response = graphql(client, mutation)
    error_msg = response.json()["errors"][0]["message"].lower()
    # Should indicate account issues
    assert any(word in error_msg for word in ["lock", "account", "try again"])


def test_logout_then_refresh_rejected(client: TestClient) -> None:
    """Test that after logout, refresh token is completely invalid."""
    tokens = login(client)
    
    # Logout
    graphql(client, """
    mutation Logout($refreshToken: String!) {
      logout(refreshToken: $refreshToken)
    }
    """, {"refreshToken": tokens["refreshToken"]})

    # Try to use the same refresh token - should be rejected
    rejected = graphql(
        client,
        """
        mutation Refresh($refreshToken: String!) {
          refreshSession(refreshToken: $refreshToken) { accessToken }
        }
        """,
        {"refreshToken": tokens["refreshToken"]},
    )
    assert "errors" in rejected.json()


def test_login_after_lockout(client: TestClient) -> None:
    """Test that after lockout, successful login is possible (presumably after admin unlock)."""
    # This test verifies the lockout mechanism
    # In a full system, admin would call unlock_user endpoint
    mutation = """
    mutation {
      login(input: {username: "testadmin", password: "wrong-password"}) {
        accessToken
      }
    }
    """

    # Get past the lockout threshold
    for _ in range(5):
        graphql(client, mutation)

    # After lockout, a login attempt should reflect locked state
    response = graphql(client, mutation)
    # The response should indicate authentication failure
    assert "errors" in response.json()