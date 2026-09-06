from typing import Literal

from langchain_core.documents import Document
from langgraph.graph import MessagesState


TaskType = Literal[
    "knowledge_query",
    "competitive_analysis",
    "industry_analysis",
    "product_comparison",
    "other",
]


ComplexityType = Literal[
    "simple",
    "complex",
]


class AgentState(MessagesState, total=False):
    """
    Agent Intelligence Platform 全局状态。

    MessagesState 自带：
        messages

    自定义字段：
        query:
            用户原始问题

        task_type:
            Router 判断的任务类型

        complexity:
            simple / complex

        plan:
            Planner 生成的研究计划

        documents:
            RAG 检索得到的文档

        answer:
            最终回答

        tool_rounds:
            已产生的 Tool Calling 轮数

            注意：
            同一个 AIMessage 中即使包含多个 Tool Call，
            也只算 1 个 Tool Round。

            例如：

            company_search(OpenAI)
            company_search(Google)

            同时出现时：

            tool_rounds += 1

            而不是 += 2
    """

    query: str

    task_type: TaskType

    complexity: ComplexityType

    plan: list[dict]

    documents: list[Document]

    answer: str

    tool_rounds: int
    
    evidence_sufficient: bool
    evidence_score: float
    evidence_gaps: list[str]