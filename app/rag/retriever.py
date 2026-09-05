from langchain_core.documents import Document

from app.rag.vector_store import load_vector_store


_vector_store = None


def get_vector_store():
    global _vector_store

    if _vector_store is None:
        _vector_store = load_vector_store()

    return _vector_store


def retrieve_documents(
    query: str,
    k: int = 6,
) -> list[Document]:
    """
    基础向量检索。
    """

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query=query,
        k=k,
    )

    return documents