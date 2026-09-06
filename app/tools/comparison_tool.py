from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm import get_llm


COMPARISON_PROMPT = """
你是一名企业 AI 产品研究分析师。

请根据提供的两个公司的结构化研究结果，
完成竞品分析。

研究主题：

{topic}


Company A:

{company_a}

Research Information:

{company_a_info}


Company B:

{company_b}

Research Information:

{company_b_info}


要求：

1. 只能基于提供的信息进行比较。
2. 不允许补充资料之外的事实。
3. 明确指出共同点。
4. 明确指出关键差异。
5. 保留 Evidence 信息。
6. 如果资料不足，需要明确说明。


输出格式：

## Comparison Summary

总体比较结论


## Common Points

- 共同点1
- 共同点2


## Key Differences

### Company A

- 特点

### Company B

- 特点


## Evidence Limitations

- 当前资料限制

"""


@tool
def compare_companies(
    company_a: str,
    company_a_info: str,
    company_b: str,
    company_b_info: str,
    topic: str,
) -> str:
    """
    比较两个公司的 AI 产品能力。

    Args:

        company_a:
            第一个公司名称

        company_a_info:
            第一个公司的结构化研究结果

        company_b:
            第二个公司名称

        company_b_info:
            第二个公司的结构化研究结果

        topic:
            比较主题


    Returns:

        结构化竞品分析报告
    """

    llm = get_llm(
        temperature=0
    )


    prompt = ChatPromptTemplate.from_template(
        COMPARISON_PROMPT
    )


    chain = (
        prompt
        |
        llm
    )


    response = chain.invoke(
        {
            "company_a": company_a,
            "company_a_info": company_a_info,

            "company_b": company_b,
            "company_b_info": company_b_info,

            "topic": topic,
        }
    )


    return response.content