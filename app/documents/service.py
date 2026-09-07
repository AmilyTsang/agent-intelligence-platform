from __future__ import annotations

import hashlib
import uuid

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from threading import (
    RLock,
)

from typing import Any


from app.documents.parser import (
    parse_pdf,
)

from app.documents.repository import (
    create_document,
    delete_document_record,
    get_document,
    get_latest_document_by_hash,
    initialize_database,
    list_documents,
    list_ready_documents,
    update_document,
)

from app.documents.vector_store import (
    add_documents,
    initialize_vector_store,
    rebuild_vector_store,
)


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

DOCUMENTS_DIR = (
    DATA_DIR
    / "documents"
)


# ============================================================
# Limits
# ============================================================

MAX_FILE_SIZE = (
    50
    * 1024
    * 1024
)


# ============================================================
# Mutation Lock
# ============================================================

_library_lock = (
    RLock()
)


# ============================================================
# Exceptions
# ============================================================


class DocumentValidationError(
    ValueError
):
    pass


class DocumentNotFoundError(
    ValueError
):
    pass


# ============================================================
# Helpers
# ============================================================


def utc_now() -> str:
    return (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


def initialize_document_library() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    initialize_database()

    initialize_vector_store()


def calculate_sha256(
    file_bytes: bytes,
) -> str:
    return hashlib.sha256(
        file_bytes
    ).hexdigest()


def sanitize_filename(
    filename: str,
) -> str:
    safe_name = (
        Path(filename)
        .name
        .strip()
    )

    if not safe_name:
        raise DocumentValidationError(
            "文件名不能为空。"
        )

    if not (
        safe_name
        .lower()
        .endswith(
            ".pdf"
        )
    ):
        raise DocumentValidationError(
            "目前只支持 PDF 文件。"
        )

    return safe_name


def validate_pdf_bytes(
    file_bytes: bytes,
) -> None:
    if not file_bytes:
        raise DocumentValidationError(
            "上传的 PDF 为空。"
        )

    if (
        len(file_bytes)
        >
        MAX_FILE_SIZE
    ):
        raise DocumentValidationError(
            "PDF 文件不能超过 50 MB。"
        )

    if not (
        file_bytes
        .lstrip()
        .startswith(
            b"%PDF"
        )
    ):
        raise DocumentValidationError(
            "文件内容不是有效的 PDF。"
        )


# ============================================================
# Serialize
# ============================================================


def serialize_document(
    record: dict[str, Any],
) -> dict[str, Any]:
    return {
        "document_id":
            record["document_id"],

        "filename":
            record["filename"],

        "status":
            record["status"],

        "pages":
            int(
                record.get(
                    "page_count",
                    0,
                )
                or 0
            ),

        "chunks":
            int(
                record.get(
                    "chunk_count",
                    0,
                )
                or 0
            ),

        "file_size":
            int(
                record.get(
                    "file_size",
                    0,
                )
                or 0
            ),

        "error":
            record.get(
                "error_message",
                "",
            )
            or "",

        "created_at":
            record.get(
                "created_at"
            ),

        "updated_at":
            record.get(
                "updated_at"
            ),
    }


# ============================================================
# List Documents
# ============================================================


def get_documents() -> list[
    dict[str, Any]
]:
    initialize_document_library()

    records = (
        list_documents()
    )

    return [
        serialize_document(
            record
        )
        for record in records
    ]


# ============================================================
# Upload Document
# ============================================================


def process_document_upload(
    *,
    filename: str,
    file_bytes: bytes,
) -> dict[str, Any]:
    initialize_document_library()

    with _library_lock:
        # ====================================================
        # Validate
        # ====================================================

        safe_filename = (
            sanitize_filename(
                filename
            )
        )

        validate_pdf_bytes(
            file_bytes
        )

        file_hash = (
            calculate_sha256(
                file_bytes
            )
        )

        # ====================================================
        # Duplicate Detection
        # ====================================================

        existing = (
            get_latest_document_by_hash(
                file_hash
            )
        )

        if (
            existing
            and
            existing.get(
                "status"
            )
            in {
                "ready",
                "processing",
            }
        ):
            return (
                serialize_document(
                    existing
                )
            )

        # ====================================================
        # Document ID
        # ====================================================

        document_id = (
            "doc_"
            + uuid.uuid4().hex[
                :16
            ]
        )

        stored_filename = (
            f"{document_id}.pdf"
        )

        file_path = (
            DOCUMENTS_DIR
            / stored_filename
        )

        now = (
            utc_now()
        )

        # ====================================================
        # Save Original PDF
        # ====================================================

        file_path.write_bytes(
            file_bytes
        )

        # ====================================================
        # Database
        # ====================================================

        create_document(
            document_id=(
                document_id
            ),

            filename=(
                safe_filename
            ),

            stored_filename=(
                stored_filename
            ),

            file_path=str(
                file_path
            ),

            file_hash=(
                file_hash
            ),

            file_size=len(
                file_bytes
            ),

            status=(
                "processing"
            ),

            created_at=(
                now
            ),
        )

        try:
            # ================================================
            # Parse + Chunk
            # ================================================

            (
                chunks,
                page_count,
            ) = parse_pdf(
                file_path=(
                    file_path
                ),

                document_id=(
                    document_id
                ),

                filename=(
                    safe_filename
                ),
            )

            # ================================================
            # Embedding + FAISS
            # ================================================

            chunk_count = (
                add_documents(
                    chunks
                )
            )

            # ================================================
            # Ready
            # ================================================

            update_document(
                document_id,

                status=(
                    "ready"
                ),

                page_count=(
                    page_count
                ),

                chunk_count=(
                    chunk_count
                ),

                error_message=(
                    ""
                ),

                updated_at=(
                    utc_now()
                ),
            )

        except Exception as exc:
            update_document(
                document_id,

                status=(
                    "failed"
                ),

                error_message=(
                    str(exc)
                ),

                updated_at=(
                    utc_now()
                ),
            )

            raise

        record = (
            get_document(
                document_id
            )
        )

        if record is None:
            raise RuntimeError(
                "Document metadata disappeared after processing."
            )

        return (
            serialize_document(
                record
            )
        )


# ============================================================
# Delete Document
# ============================================================


def delete_document_from_library(
    document_id: str,
) -> dict[str, object]:
    initialize_document_library()

    with _library_lock:
        # ====================================================
        # Target
        # ====================================================

        target = (
            get_document(
                document_id
            )
        )

        if target is None:
            raise DocumentNotFoundError(
                f"文档不存在：{document_id}"
            )

        # ====================================================
        # Remaining Ready Documents
        # ====================================================

        ready_records = (
            list_ready_documents()
        )

        remaining_records = [
            record
            for record
            in ready_records
            if (
                record.get(
                    "document_id"
                )
                != document_id
            )
        ]

        # ====================================================
        # Parse Remaining Documents
        # ====================================================

        remaining_chunks = []

        for record in (
            remaining_records
        ):
            remaining_document_id = (
                str(
                    record[
                        "document_id"
                    ]
                )
            )

            filename = (
                str(
                    record[
                        "filename"
                    ]
                )
            )

            file_path = (
                Path(
                    record[
                        "file_path"
                    ]
                )
            )

            if not file_path.exists():
                raise RuntimeError(
                    (
                        "无法重建向量库，"
                        "原始文件不存在："
                        f"{filename}"
                    )
                )

            (
                chunks,
                _,
            ) = parse_pdf(
                file_path=(
                    file_path
                ),

                document_id=(
                    remaining_document_id
                ),

                filename=(
                    filename
                ),
            )

            remaining_chunks.extend(
                chunks
            )

        # ====================================================
        # Rebuild FAISS
        # ====================================================

        rebuilt_chunk_count = (
            rebuild_vector_store(
                remaining_chunks
            )
        )

        # ====================================================
        # Delete Database Record
        # ====================================================

        deleted = (
            delete_document_record(
                document_id
            )
        )

        if not deleted:
            raise RuntimeError(
                "删除文档数据库记录失败。"
            )

        # ====================================================
        # Delete Original PDF
        # ====================================================

        target_file_path = (
            Path(
                target[
                    "file_path"
                ]
            )
        )

        try:
            if target_file_path.exists():
                target_file_path.unlink()

        except OSError as exc:
            print(
                "[Documents] Warning: "
                "metadata deleted but "
                "original PDF could not "
                f"be removed: {exc}"
            )

        # ====================================================
        # Result
        # ====================================================

        return {
            "document_id":
                document_id,

            "filename":
                str(
                    target[
                        "filename"
                    ]
                ),

            "deleted":
                True,

            "remaining_documents":
                len(
                    remaining_records
                ),

            "remaining_chunks":
                rebuilt_chunk_count,
        }