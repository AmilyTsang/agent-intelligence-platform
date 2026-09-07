from __future__ import annotations

from langchain_core.documents import Document

from app.documents.vector_store import (
    similarity_search,
    similarity_search_with_score,
)


# ============================================================
# General Retrieval
# ============================================================


def search_uploaded_documents(
    query: str,
    *,
    k: int = 8,
) -> list[Document]:
    """
    Search all uploaded ready documents.

    Every conversation shares this same persistent
    document library.
    """

    return similarity_search(
        query,
        k=k,
    )


# ============================================================
# Retrieval With Scores
# ============================================================


def search_uploaded_documents_with_score(
    query: str,
    *,
    k: int = 8,
):
    return (
        similarity_search_with_score(
            query,
            k=k,
        )
    )


# ============================================================
# Search One Named Document
# ============================================================


def search_document_by_filename(
    *,
    filename: str,
    query: str,
    k: int = 8,
    fetch_k: int = 40,
) -> list[Document]:
    """
    MVP helper.

    Retrieve a wider pool, then keep evidence
    from the requested filename.

    This is useful while the existing Agent tools
    are still company-oriented.
    """

    normalized_filename = (
        filename
        .strip()
        .lower()
    )


    candidates = (
        similarity_search(
            query,
            k=max(
                fetch_k,
                k,
            ),
        )
    )


    results: list[
        Document
    ] = []


    for document in candidates:
        candidate_filename = (
            str(
                document.metadata.get(
                    "filename",
                    "",
                )
            )
            .lower()
        )


        if (
            normalized_filename
            in candidate_filename
        ):
            results.append(
                document
            )


        if len(results) >= k:
            break


    return results