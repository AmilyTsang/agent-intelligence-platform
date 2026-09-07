from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


# ============================================================
# Research Request
# ============================================================


class ResearchRequest(
    BaseModel
):
    query: str = Field(
        min_length=1,

        max_length=5000,

        description=(
            "用户研究问题"
        ),

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


class PlanStepResponse(
    BaseModel
):
    step_id: int

    action: str

    description: str


# ============================================================
# Evidence
# ============================================================


class EvidenceResponse(
    BaseModel
):
    evaluated: bool = False

    sufficient: (
        bool
        | None
    ) = None

    score: (
        float
        | None
    ) = None

    gaps: list[str] = Field(
        default_factory=list
    )


# ============================================================
# Retry
# ============================================================


class RetryQueryResponse(
    BaseModel
):
    company: str = ""

    query: str = ""

    gap: str = ""


class RetryResponse(
    BaseModel
):
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


class EvidenceTrackingResponse(
    BaseModel
):
    unique: int = 0

    new: int = 0

    duplicates: int = 0

    last_new: int = 0

    last_duplicates: int = 0


# ============================================================
# Tool Trace
# ============================================================


class ToolTraceItem(
    BaseModel
):
    index: int

    name: str

    content: str = ""


# ============================================================
# Token Usage
# ============================================================


class TokenUsageResponse(
    BaseModel
):
    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    llm_calls: int = 0


# ============================================================
# Timing
# ============================================================


class TimingResponse(
    BaseModel
):
    total_seconds: float = 0.0

    total_ms: float = 0.0


# ============================================================
# Research Response
# ============================================================


class ResearchResponse(
    BaseModel
):
    query: str

    task_type: (
        Literal[
            "knowledge_query",
            "competitive_analysis",
            "industry_analysis",
            "product_comparison",
            "other",
        ]
        | str
        | None
    ) = None

    complexity: (
        Literal[
            "simple",
            "complex",
        ]
        | str
        | None
    ) = None

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

    token_usage: (
        TokenUsageResponse
    )

    timing: TimingResponse


# ============================================================
# Documents
# ============================================================


class DocumentResponse(
    BaseModel
):
    document_id: str

    filename: str

    status: Literal[
        "processing",
        "ready",
        "failed",
    ] | str

    pages: int = 0

    chunks: int = 0

    file_size: int = 0

    error: str = ""

    created_at: (
        str
        | None
    ) = None

    updated_at: (
        str
        | None
    ) = None

# ============================================================
# Document Delete
# ============================================================


class DocumentDeleteResponse(
    BaseModel
):
    document_id: str

    filename: str

    deleted: bool

    remaining_documents: int = 0

    remaining_chunks: int = 0