from __future__ import annotations

import sqlite3

from contextlib import contextmanager

from pathlib import Path

from typing import Any


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DATA_DIR = (
    PROJECT_ROOT
    / "data"
)

DATABASE_PATH = (
    DATA_DIR
    / "app.db"
)


# ============================================================
# Database Connection
# ============================================================


@contextmanager
def get_connection():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = (
        sqlite3.Row
    )

    try:
        yield connection

        connection.commit()

    except Exception:
        connection.rollback()

        raise

    finally:
        connection.close()


# ============================================================
# Initialize Database
# ============================================================


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                status TEXT NOT NULL DEFAULT 'processing',
                page_count INTEGER NOT NULL DEFAULT 0,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                file_size INTEGER NOT NULL DEFAULT 0,
                error_message TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_documents_status
            ON documents(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_documents_hash
            ON documents(file_hash)
            """
        )


# ============================================================
# Create Document
# ============================================================


def create_document(
    *,
    document_id: str,
    filename: str,
    stored_filename: str,
    file_path: str,
    file_hash: str,
    file_size: int,
    status: str,
    created_at: str,
) -> dict[str, Any]:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                filename,
                stored_filename,
                file_path,
                file_hash,
                status,
                page_count,
                chunk_count,
                file_size,
                error_message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, '', ?, ?)
            """,
            (
                document_id,
                filename,
                stored_filename,
                file_path,
                file_hash,
                status,
                file_size,
                created_at,
                created_at,
            ),
        )

    document = get_document(
        document_id
    )

    if document is None:
        raise RuntimeError(
            "Failed to create document record."
        )

    return document


# ============================================================
# Update Document
# ============================================================


def update_document(
    document_id: str,
    *,
    status: str | None = None,
    page_count: int | None = None,
    chunk_count: int | None = None,
    error_message: str | None = None,
    updated_at: str,
) -> None:
    assignments = [
        "updated_at = ?"
    ]

    values: list[Any] = [
        updated_at
    ]

    if status is not None:
        assignments.append(
            "status = ?"
        )

        values.append(
            status
        )

    if page_count is not None:
        assignments.append(
            "page_count = ?"
        )

        values.append(
            page_count
        )

    if chunk_count is not None:
        assignments.append(
            "chunk_count = ?"
        )

        values.append(
            chunk_count
        )

    if error_message is not None:
        assignments.append(
            "error_message = ?"
        )

        values.append(
            error_message
        )

    values.append(
        document_id
    )

    sql = f"""
        UPDATE documents
        SET {", ".join(assignments)}
        WHERE document_id = ?
    """

    with get_connection() as connection:
        connection.execute(
            sql,
            values,
        )


# ============================================================
# Get One Document
# ============================================================


def get_document(
    document_id: str,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = ?
            """,
            (
                document_id,
            ),
        ).fetchone()

    if row is None:
        return None

    return dict(
        row
    )


# ============================================================
# Get Document By Hash
# ============================================================


def get_latest_document_by_hash(
    file_hash: str,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE file_hash = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (
                file_hash,
            ),
        ).fetchone()

    if row is None:
        return None

    return dict(
        row
    )


# ============================================================
# List All Documents
# ============================================================


def list_documents(
    *,
    include_failed: bool = True,
) -> list[dict[str, Any]]:
    sql = """
        SELECT *
        FROM documents
    """

    values: list[Any] = []

    if not include_failed:
        sql += """
            WHERE status != ?
        """

        values.append(
            "failed"
        )

    sql += """
        ORDER BY created_at DESC
    """

    with get_connection() as connection:
        rows = connection.execute(
            sql,
            values,
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# List Ready Documents
# ============================================================


def list_ready_documents() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE status = 'ready'
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# Delete Document Record
# ============================================================


def delete_document_record(
    document_id: str,
) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM documents
            WHERE document_id = ?
            """,
            (
                document_id,
            ),
        )

        deleted = (
            cursor.rowcount > 0
        )

    return deleted