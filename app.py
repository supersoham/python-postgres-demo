import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    return psycopg.connect(DATABASE_URL, connect_timeout=3)


@app.get("/")
def home():
    return jsonify(message="Python API is running!")


@app.get("/health")
def health():
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return jsonify(status="ok", database="connected")
    except psycopg.Error:
        return jsonify(status="error", database="unavailable"), 503


@app.post("/visits")
def add_visit():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        cur.execute("INSERT INTO visits DEFAULT VALUES RETURNING id, visited_at")
        visit_id, visited_at = cur.fetchone()

    return jsonify(id=visit_id, visited_at=visited_at.isoformat()), 201


@app.get("/visits")
def list_visits():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id SERIAL PRIMARY KEY,
                    visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        cur.execute("SELECT id, visited_at FROM visits ORDER BY id")
        rows = cur.fetchall()

    return jsonify([{"id": row[0], "visited_at": row[1].isoformat()} for row in rows])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
