from langchain_core.documents import Document

from app.rag.vector_store import load_vector_store


def search_company_documents(
    company: str,
    query: str,
    k: int = 4,
) -> list[Document]:
    """
    在指定公司的知识库资料中进行向量检索。

    Args:
        company:
            公司名称，例如 OpenAI、Google

        query:
            具体研究问题

        k:
            最终返回的文档数量

    Returns:
        与问题最相关的 Document 列表
    """

    vector_store = load_vector_store()

    company_key = company.strip().lower()

    print(
        f"[Search] company={company_key}, "
        f"query={query}, k={k}"
    )

    documents = vector_store.similarity_search(
        query=query,
        k=k,
        filter={
            "company": company_key,
        },
        fetch_k=max(20, k * 5),
    )

    print(
        f"[Search] retrieved={len(documents)}"
    )

    return documents