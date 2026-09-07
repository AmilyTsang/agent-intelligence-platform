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
    # ========================================================
    # User Request
    # ========================================================

    query: str

    # ========================================================
    # Router
    # ========================================================

    task_type: TaskType
    complexity: ComplexityType

    # ========================================================
    # Planner
    # ========================================================

    plan: list[dict]

    # ========================================================
    # RAG
    # ========================================================

    documents: list[Document]

    # ========================================================
    # Final Answer
    # ========================================================

    answer: str

    # ========================================================
    # Tool Loop
    # ========================================================

    tool_rounds: int

    # ========================================================
    # Evidence Checker
    # ========================================================

    evidence_sufficient: bool
    evidence_score: float
    evidence_gaps: list[str]

    # ========================================================
    # Evidence-driven Retry
    # ========================================================

    retry_count: int
    retry_queries: list[dict]
    retry_reason: str

    # ========================================================
    # Evidence Tracking
    # ========================================================

    # 整个 Research Run 已经见过的唯一 Evidence ID
    evidence_ids: list[str]

    # 整个 Research Run 累计新增 Evidence 数
    new_evidence_count: int

    # 整个 Research Run 累计重复 Evidence 数
    duplicate_evidence_count: int

    # 最近一次 ToolNode 执行新增 Evidence 数
    last_new_evidence_count: int

    # 最近一次 ToolNode 执行重复 Evidence 数
    last_duplicate_evidence_count: int