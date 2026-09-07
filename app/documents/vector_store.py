from __future__ import annotations

import os

from functools import lru_cache

from pathlib import Path

from threading import RLock


from langchain_community.vectorstores import (
    FAISS,
)

from langchain_core.documents import (
    Document,
)


try:
    from langchain_huggingface import (
        HuggingFaceEmbeddings,
    )

except ImportError:
    from langchain_community.embeddings import (
        HuggingFaceEmbeddings,
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

VECTOR_STORE_DIR = (
    DATA_DIR
    / "vector_store"
)


# ============================================================
# Embedding Configuration
# ============================================================

EMBEDDING_MODEL_NAME = (
    os.getenv(
        "EMBEDDING_MODEL_NAME",
        "BAAI/bge-m3",
    )
)

EMBEDDING_DEVICE = (
    os.getenv(
        "EMBEDDING_DEVICE",
        "cpu",
    )
)


# ============================================================
# Runtime State
# ============================================================

_vector_store: (
    FAISS
    | None
) = None

_store_lock = (
    RLock()
)


# ============================================================
# Initialize
# ============================================================


def initialize_vector_store() -> None:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    VECTOR_STORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# Embedding Model
# ============================================================


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=(
            EMBEDDING_MODEL_NAME
        ),

        model_kwargs={
            "device":
                EMBEDDING_DEVICE,
        },

        encode_kwargs={
            "normalize_embeddings":
                True,
        },
    )


# ============================================================
# Exists
# ============================================================


def vector_store_exists() -> bool:
    index_file = (
        VECTOR_STORE_DIR
        / "index.faiss"
    )

    metadata_file = (
        VECTOR_STORE_DIR
        / "index.pkl"
    )

    return (
        index_file.exists()
        and
        metadata_file.exists()
    )


# ============================================================
# Load
# ============================================================


def load_vector_store() -> FAISS | None:
    global _vector_store

    with _store_lock:
        if (
            _vector_store
            is not None
        ):
            return _vector_store

        if not vector_store_exists():
            return None

        embeddings = (
            get_embeddings()
        )

        _vector_store = (
            FAISS.load_local(
                folder_path=str(
                    VECTOR_STORE_DIR
                ),

                embeddings=embeddings,

                allow_dangerous_deserialization=True,
            )
        )

        return _vector_store


# ============================================================
# Add Documents
# ============================================================


def add_documents(
    documents: list[Document],
) -> int:
    global _vector_store

    if not documents:
        return 0

    initialize_vector_store()

    with _store_lock:
        store = (
            load_vector_store()
        )

        embeddings = (
            get_embeddings()
        )

        if store is None:
            store = (
                FAISS.from_documents(
                    documents=documents,
                    embedding=embeddings,
                )
            )

            _vector_store = (
                store
            )

        else:
            store.add_documents(
                documents
            )

        store.save_local(
            str(
                VECTOR_STORE_DIR
            )
        )

        _vector_store = (
            store
        )

    return len(
        documents
    )


# ============================================================
# Rebuild Vector Store
# ============================================================


def rebuild_vector_store(
    documents: list[Document],
) -> int:
    """
    Completely rebuild FAISS.

    Used after deleting a document so that
    deleted document vectors cannot remain
    inside the index.
    """

    global _vector_store

    initialize_vector_store()

    with _store_lock:
        index_file = (
            VECTOR_STORE_DIR
            / "index.faiss"
        )

        metadata_file = (
            VECTOR_STORE_DIR
            / "index.pkl"
        )

        # ====================================================
        # No Documents Left
        # ====================================================

        if not documents:
            _vector_store = None

            if index_file.exists():
                index_file.unlink()

            if metadata_file.exists():
                metadata_file.unlink()

            return 0

        # ====================================================
        # Build New Index
        # ====================================================

        embeddings = (
            get_embeddings()
        )

        new_store = (
            FAISS.from_documents(
                documents=documents,
                embedding=embeddings,
            )
        )

        new_store.save_local(
            str(
                VECTOR_STORE_DIR
            )
        )

        _vector_store = (
            new_store
        )

        return len(
            documents
        )


# ============================================================
# Similarity Search
# ============================================================


def similarity_search(
    query: str,
    *,
    k: int = 8,
) -> list[Document]:
    if not query.strip():
        return []

    store = (
        load_vector_store()
    )

    if store is None:
        return []

    with _store_lock:
        return store.similarity_search(
            query=query,
            k=k,
        )


# ============================================================
# Similarity Search With Score
# ============================================================


def similarity_search_with_score(
    query: str,
    *,
    k: int = 8,
):
    if not query.strip():
        return []

    store = (
        load_vector_store()
    )

    if store is None:
        return []

    with _store_lock:
        return (
            store.similarity_search_with_score(
                query=query,
                k=k,
            )
        )


# ============================================================
# Retriever
# ============================================================


def get_retriever(
    *,
    k: int = 8,
):
    store = (
        load_vector_store()
    )

    if store is None:
        return None

    return store.as_retriever(
        search_kwargs={
            "k":
                k,
        }
    )