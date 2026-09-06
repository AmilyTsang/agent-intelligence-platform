import json

from langchain_core.tools import tool

from app.tools.extractor import extract_information


@tool
def extract_company_info(
    company: str,
    topic: str,
    evidence: str,
) -> str:
    """
    从 company_search 返回的企业资料中提取结构化研究信息。

    调用此工具前，应先通过 company_search 获取对应公司的 Evidence。

    Args:
        company:
            企业名称，例如 OpenAI、Google。

        topic:
            需要分析的研究主题，例如 Agent Tools。

        evidence:
            company_search 返回的完整 Evidence 内容。

    Returns:
        JSON 格式的企业结构化研究结果。
    """

    print(
        f"[Tool: extract_company_info] "
        f"company={company}, topic={topic}"
    )

    result = extract_information(
        company=company,
        topic=topic,
        evidence=evidence,
    )

    return json.dumps(
        result,
        ensure_ascii=False,
    )