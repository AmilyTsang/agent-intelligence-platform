from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


# ============================================================
# Request
# ============================================================


class ResearchRequest(BaseModel):
    """
    Research Agent API 请求。
    """

    query: str = Field(
        min_length=1,
        max_length=5000,
        description="用户研究问题",
        examples=[
            (
                "比较 OpenAI 和 Google "
                "在 Agent Tools 设计上的共同点和差异。"
            )
        ],
    )


# ============================================================
# Plan
# ============================================================


class PlanStepResponse(BaseModel):
    """
    Research Plan 单个步骤。
    """

    step_id: int

    action: str

    description: str


# ============================================================
# Evidence
# ============================================================


class EvidenceResponse(BaseModel):
    """
    Evidence Checker 结果。
    """

    evaluated: bool = False

    sufficient: bool | None = None

    score: float | None = None

    gaps: list[str] = Field(
        default_factory=list
    )


# ============================================================
# Retry
# ============================================================


class RetryQueryResponse(BaseModel):
    """
    Query Rewriter 生成的单条 Retry Query。
    """

    company: str

    query: str

    gap: str = ""


class RetryResponse(BaseModel):
    """
    Evidence-driven Retry 状态。
    """

    count: int = 0

    queries: list[
        RetryQueryResponse
    ] = Field(
        default_factory=list
    )

    reason: str = ""


# ============================================================
# Evidence Tracking
# ============================================================


class EvidenceTrackingResponse(BaseModel):
    """
    Context Engineering Evidence 统计。
    """

    unique: int = 0

    new: int = 0

    duplicates: int = 0

    last_new: int = 0

    last_duplicates: int = 0


# ============================================================
# Tool Trace
# ============================================================


class ToolTraceItem(BaseModel):
    """
    实际已经执行完成的 Tool。

    注意：
    这里记录 ToolMessage，
    而不是 AIMessage 中仅仅提出的 tool_calls。

    因此 Tool Loop Limit 阻止的 Tool Call
    不会被误认为实际执行。
    """

    index: int

    name: str


# ============================================================
# Token Usage
# ============================================================


class TokenUsageResponse(BaseModel):
    """
    单次完整 Research Run 的 LLM Token 用量。

    input_tokens:
        所有 LLM 调用累计输入 Token。

    output_tokens:
        所有 LLM 调用累计输出 Token。

    total_tokens:
        input_tokens + output_tokens。

    llm_calls:
        本次 Research Run 中实际完成的 LLM 调用次数。
    """

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    llm_calls: int = 0


# ============================================================
# Timing
# ============================================================


class TimingResponse(BaseModel):
    """
    单次完整 Research Run 的端到端执行时间。

    包含：
    Router
    Planner
    LLM
    RAG
    Tools
    Evidence Checker
    Retry
    Finalize
    等整个 Graph 执行过程。
    """

    total_seconds: float = 0.0

    total_ms: float = 0.0


# ============================================================
# Response
# ============================================================


class ResearchResponse(BaseModel):
    """
    Research Agent 对外稳定响应结构。

    React 前端之后只依赖这一层，
    不直接依赖 LangGraph AgentState。
    """

    query: str

    task_type: Literal[
        "knowledge_query",
        "competitive_analysis",
        "industry_analysis",
        "product_comparison",
        "other",
    ] | str | None = None

    complexity: Literal[
        "simple",
        "complex",
    ] | str | None = None

    plan: list[
        PlanStepResponse
    ] = Field(
        default_factory=list
    )

    answer: str = ""

    tool_trace: list[
        ToolTraceItem
    ] = Field(
        default_factory=list
    )

    tool_rounds: int = 0

    evidence: EvidenceResponse

    retry: RetryResponse

    evidence_tracking: (
        EvidenceTrackingResponse
    )

    # ========================================================
    # Observability
    # ========================================================

    token_usage: TokenUsageResponse

    timing: TimingResponse