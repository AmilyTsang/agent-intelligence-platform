from langchain_core.prompts import ChatPromptTemplate

from app.agent.state import AgentState
from app.services.llm import get_llm


ANSWER_PROMPT = """
你是企业 AI 产品研究助手。

请严格基于下面提供的企业资料回答用户问题。

如果资料不足以支持某个结论，请明确说明：
“当前资料不足以支持该结论。”

不要凭空补充事实。

用户问题：

{query}


研究计划：

{plan}


检索证据：

{context}


回答要求：

1. 优先回答用户的核心问题。
2. 对比较类问题使用清晰的结构。
3. 区分事实与分析判断。
4. 对重要事实标记来源。
5. 不得虚构未出现在 Context 中的数据。
"""


def format_context(documents) -> str:
    blocks = []

    for index, doc in enumerate(
        documents,
        start=1,
    ):
        source = doc.metadata.get(
            "source",
            "unknown",
        )

        page = doc.metadata.get(
            "page",
            "unknown",
        )

        company = doc.metadata.get(
            "company",
            "unknown",
        )

        blocks.append(
            f"""
[Evidence {index}]
Company: {company}
Source: {source}
Page: {page}

{doc.page_content}
""".strip()
        )

    return "\n\n".join(blocks)


def answer_node(
    state: AgentState,
) -> AgentState:

    llm = get_llm(
        temperature=0.1
    )

    documents = state.get(
        "documents",
        [],
    )

    context = format_context(
        documents
    )

    plan = state.get(
        "plan",
        [],
    )

    prompt = ChatPromptTemplate.from_template(
        ANSWER_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "query": state["query"],
            "plan": plan,
            "context": context,
        }
    )

    return {
        "answer": response.content,
    }