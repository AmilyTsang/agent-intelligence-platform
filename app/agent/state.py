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


class AgentState(
    MessagesState,
    total=False,
):
    # 用户原始问题
    query: str

    # Router 结果
    task_type: TaskType
    complexity: ComplexityType

    # Planner 结果
    plan: list[dict]

    # 原有简单 RAG 链路使用
    documents: list[Document]

    # 最终答案
    answer: str