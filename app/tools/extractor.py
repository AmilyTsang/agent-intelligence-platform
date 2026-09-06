from typing import Dict, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm import get_llm


def extract_information(
    company: str,
    topic: str,
    evidence: str,
) -> Dict:
    """
    从企业资料中提取指定主题的信息。

    Args:
        company:
            公司名称

        topic:
            研究主题

        evidence:
            检索得到的文档内容

    Returns:
        结构化信息 Dict
    """

    llm = get_llm(
        temperature=0
    )

    parser = JsonOutputParser()


    prompt = ChatPromptTemplate.from_template(
        """
你是一名企业 AI 产品研究分析师。

请严格根据下面提供的 Evidence，
提取 {company} 关于 {topic} 的信息。

要求：

1. 只能使用 Evidence 中的信息。
2. 不允许补充外部知识。
3. 如果 Evidence 没有相关内容，填写：
   "资料不足"
4. 输出必须是合法 JSON。


JSON格式：

{{
    "company": "{company}",
    "topic": "{topic}",
    "key_findings": [
        "..."
    ],
    "technical_details": [
        "..."
    ],
    "limitations": [
        "..."
    ],
    "evidence": [
        {{
            "source": "",
            "page": "",
            "content": ""
        }}
    ]
}}


Evidence:

{evidence}


{format_instructions}
"""
    )


    chain = (
        prompt
        |
        llm
        |
        parser
    )


    result = chain.invoke(
        {
            "company": company,
            "topic": topic,
            "evidence": evidence,
            "format_instructions":
                parser.get_format_instructions(),
        }
    )


    return result