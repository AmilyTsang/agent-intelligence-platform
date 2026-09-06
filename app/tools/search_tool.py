from langchain_core.tools import tool

from app.tools.search import (
    search_company_documents,
)


@tool
def company_search(
    company: str,
    query: str,
) -> str:
    """
    搜索指定公司的企业知识库资料。

    Args:

        company:
            企业名称，例如 OpenAI、Google

        query:
            需要查询的问题

    Returns:

        包含来源信息的 Evidence
    """


    documents = search_company_documents(
        company=company,
        query=query,
        k=4,
    )


    if not documents:

        return (
            f"没有找到 {company} "
            "相关资料。"
        )


    results = []


    for index, doc in enumerate(
        documents,
        start=1,
    ):

        results.append(
            f"""
Evidence {index}

Company:
{doc.metadata.get("company")}

Source:
{doc.metadata.get("source")}

Page:
{doc.metadata.get("page")}


Content:

{doc.page_content[:1500]}
"""
        )


    return "\n\n".join(results)