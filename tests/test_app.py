import os
from unittest.mock import MagicMock, patch

# The app reads DATABASE_URL when it is imported.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://appuser:devpass@localhost:5432/appdb",
)

from app import app


def test_home_endpoint():
    """The home endpoint should return a success message."""
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Python API is running!"
    }


def test_health_endpoint():
    """The health endpoint should report a working database."""
    client = app.test_client()

    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = (1,)

    with patch("app.psycopg.connect", return_value=connection):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "connected",
    }

def test_health_endpoint_database_failure():
    """The health endpoint should return 503 when the database is unavailable."""
    import psycopg
    from unittest.mock import patch

    client = app.test_client()

    with patch(
        "app.psycopg.connect",
        side_effect=psycopg.OperationalError("Database unavailable"),
    ):
        response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "error",
        "database": "unavailable",
    }

def test_create_visit():
    """POST /visits should create a visit and return its ID and timestamp."""
    from datetime import datetime, timezone

    client = app.test_client()
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    visited_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    cursor.fetchone.return_value = (42, visited_at)

    with patch("app.get_connection", return_value=connection):
        response = client.post("/visits")

    assert response.status_code == 201
    assert response.get_json() == {
        "id": 42,
        "visited_at": "2026-01-01T00:00:00+00:00",
    }

    assert cursor.execute.call_count == 2


def test_list_visits():
    """GET /visits should return visits ordered by ID."""
    from datetime import datetime, timezone

    client = app.test_client()
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    first_visit = datetime(2026, 1, 1, tzinfo=timezone.utc)
    second_visit = datetime(2026, 1, 2, tzinfo=timezone.utc)

    cursor.fetchall.return_value = [
        (1, first_visit),
        (2, second_visit),
    ]

    with patch("app.get_connection", return_value=connection):
        response = client.get("/visits")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 1,
            "visited_at": "2026-01-01T00:00:00+00:00",
        },
        {
            "id": 2,
            "visited_at": "2026-01-02T00:00:00+00:00",
        },
    ]

    assert cursor.execute.call_count == 2