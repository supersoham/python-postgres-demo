import os

import psycopg
import pytest

from app import app

DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture
def client_with_clean_database():
    """Use a dedicated test database and clear its visits before each test."""
    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        cur.execute("TRUNCATE TABLE visits RESTART IDENTITY")

    yield app.test_client()


def test_health_with_real_postgres(client_with_clean_database):
    response = client_with_clean_database.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "database": "connected",
    }


def test_create_and_list_visits_with_real_postgres(
    client_with_clean_database,
):
    client = client_with_clean_database

    create_response = client.post("/visits")

    assert create_response.status_code == 201
    created_visit = create_response.get_json()
    assert isinstance(created_visit["id"], int)
    assert created_visit["visited_at"]

    list_response = client.get("/visits")

    assert list_response.status_code == 200
    visits = list_response.get_json()
    assert len(visits) == 1
    assert visits[0]["id"] == created_visit["id"]
    assert visits[0]["visited_at"] == created_visit["visited_at"]
