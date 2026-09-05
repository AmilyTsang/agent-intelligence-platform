from typing import Literal, TypedDict

from langchain_core.documents import Document


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


class AgentState(TypedDict, total=False):
    # 原始请求
    query: str

    # Router结果
    task_type: TaskType
    complexity: ComplexityType

    # Planner结果
    plan: list[dict]

    # 检索结果
    documents: list[Document]

    # 最终回答
    answer: str