from langchain_core.tools import tool

from app.tools.search import (
    build_evidence_id,
    search_company_documents,
)


@tool
def company_search(
    company: str,
    query: str,
    k: int = 4,
) -> str:
    """
    从指定公司的本地知识库中搜索企业技术资料。

    Args:
        company:
            公司名称，例如 OpenAI、Google。

        query:
            检索主题。

        k:
            返回 Evidence 数量。

    Returns:
        带有 evidence_id、source、page、
        chunk_id 的 Evidence 文本。
    """

    print(
        "\n"
        f"[Tool: company_search] "
        f"company={company}, "
        f"query={query}, "
        f"k={k}"
    )

    documents = search_company_documents(
        company=company,
        query=query,
        k=k,
    )

    if not documents:

        return (
            "No evidence found "
            f"for company={company}, "
            f"query={query}."
        )

    evidence_blocks = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        metadata = (
            document.metadata
            or {}
        )

        source = metadata.get(
            "source",
            "unknown",
        )

        page = metadata.get(
            "page",
            "unknown",
        )

        chunk_id = metadata.get(
            "chunk_id",
            "unknown",
        )

        evidence_id = build_evidence_id(
            document
        )

        content = (
            document.page_content
            or ""
        ).strip()

        if len(content) > 1500:
            content = (
                content[:1500]
                + "\n...[truncated]"
            )

        block = f"""
<<EVIDENCE_START>>
Evidence {index}

company: {company}
source: {source}
page: {page}
chunk_id: {chunk_id}
evidence_id: {evidence_id}

content:
{content}
<<EVIDENCE_END>>
""".strip()

        evidence_blocks.append(
            block
        )

    result = "\n\n".join(
        evidence_blocks
    )

    print(
        "[Tool: company_search] "
        f"returned={len(documents)} "
        f"evidence blocks"
    )

    return result