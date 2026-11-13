from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.database.base import Base
from app.main import create_app
from app.modules.auth.models import User
from app.core.permissions import UserRole
from app.core.security import hash_password


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    settings = Settings(
        environment="test",
        secret_key="test-signing-key-with-at-least-32-characters",
        storage_dir=tmp_path,
        REMEMBER_ME_ENABLED=True,
    )
    application = create_app(settings)
    Base.metadata.create_all(application.state.engine)
    with application.state.session_factory() as session:
        session.add(
            User(
                username="testadmin",
                email="testadmin@example.test",
                password_hash=hash_password("Correct-Horse-Battery-Staple!2024"),
                role=UserRole.ADMINISTRATOR,
            )
        )
        session.commit()
    with TestClient(application) as test_client:
        yield test_client
    application.state.engine.dispose()


def graphql(client: TestClient, query: str, variables: dict | None = None, token: str | None = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post(
        "/graphql",
        json={"query": query, "variables": variables or {}},
        headers=headers,
    )