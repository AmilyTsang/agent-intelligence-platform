from time import perf_counter

import traceback


from fastapi import (
    FastAPI,
    HTTPException,
)

from fastapi.concurrency import (
    run_in_threadpool,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)


from langchain_community.callbacks.manager import (
    get_openai_callback,
)

from langchain_core.messages import (
    ToolMessage,
)


from app.agent.graph import (
    research_graph,
)

from app.api.documents import (
    router as documents_router,
)

from app.api.schemas import (
    EvidenceResponse,
    EvidenceTrackingResponse,
    PlanStepResponse,
    ResearchRequest,
    ResearchResponse,
    RetryQueryResponse,
    RetryResponse,
    ToolTraceItem,
)

from app.documents.service import (
    initialize_document_library,
)


# ============================================================
# Initialize Persistent Document Library
# ============================================================

initialize_document_library()


# ============================================================
# FastAPI
# ============================================================

app = FastAPI(
    title=(
        "Agent Intelligence Platform"
    ),

    version=(
        "1.0.0"
    ),

    description=(
        "Evidence-driven enterprise "
        "document research agent."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# Routers
# ============================================================

app.include_router(
    documents_router
)


# ============================================================
# Health
# ============================================================


@app.get(
    "/health"
)
async def health():
    return {
        "status":
            "ok"
    }


# ============================================================
# Tool Trace
# ============================================================


def collect_tool_trace(
    messages,
) -> list[ToolTraceItem]:
    trace: list[
        ToolTraceItem
    ] = []


    for index, message in enumerate(
        messages or [],
        start=1,
    ):
        if not isinstance(
            message,
            ToolMessage,
        ):
            continue


        trace.append(
            ToolTraceItem(
                index=index,

                name=(
                    message.name
                    or "tool"
                ),

                content=str(
                    message.content
                    or ""
                ),
            )
        )


    return trace


# ============================================================
# Graph Runner
# ============================================================


def run_research_graph(
    query: str,
):
    initial_state = {
        "query":
            query,

        "messages":
            [],

        "tool_rounds":
            0,

        "retry_count":
            0,

        "retry_queries":
            [],

        "evidence_ids":
            [],

        "new_evidence_count":
            0,

        "duplicate_evidence_count":
            0,

        "last_new_evidence_count":
            0,

        "last_duplicate_evidence_count":
            0,
    }


    return (
        research_graph.invoke(
            initial_state
        )
    )


# ============================================================
# Metrics
# ============================================================


def run_research_with_metrics(
    query: str,
):
    started_at = (
        perf_counter()
    )


    with get_openai_callback() as callback:
        result = (
            run_research_graph(
                query
            )
        )


    elapsed_seconds = (
        perf_counter()
        -
        started_at
    )


    token_usage = {
        "input_tokens":
            int(
                callback.prompt_tokens
                or 0
            ),

        "output_tokens":
            int(
                callback.completion_tokens
                or 0
            ),

        "total_tokens":
            int(
                callback.total_tokens
                or 0
            ),

        "llm_calls":
            int(
                callback.successful_requests
                or 0
            ),
    }


    timing = {
        "total_seconds":
            round(
                elapsed_seconds,
                3,
            ),

        "total_ms":
            round(
                elapsed_seconds
                * 1000,
                1,
            ),
    }


    return (
        result,
        token_usage,
        timing,
    )


# ============================================================
# Build API Response
# ============================================================


def build_response(
    query: str,
    state: dict,
    token_usage: dict | None = None,
    timing: dict | None = None,
) -> ResearchResponse:
    token_usage = (
        token_usage
        or {
            "input_tokens":
                0,

            "output_tokens":
                0,

            "total_tokens":
                0,

            "llm_calls":
                0,
        }
    )


    timing = (
        timing
        or {
            "total_seconds":
                0.0,

            "total_ms":
                0.0,
        }
    )


    # ========================================================
    # Plan
    # ========================================================

    raw_plan = (
        state.get(
            "plan"
        )
        or []
    )


    plan: list[
        PlanStepResponse
    ] = []


    for index, step in enumerate(
        raw_plan,
        start=1,
    ):
        if isinstance(
            step,
            dict,
        ):
            plan.append(
                PlanStepResponse(
                    step_id=int(
                        step.get(
                            "step_id",
                            index,
                        )
                    ),

                    action=str(
                        step.get(
                            "action",
                            "",
                        )
                    ),

                    description=str(
                        step.get(
                            "description",
                            "",
                        )
                    ),
                )
            )

        else:
            plan.append(
                PlanStepResponse(
                    step_id=index,

                    action="research",

                    description=str(
                        step
                    ),
                )
            )


    # ========================================================
    # Evidence
    # ========================================================

    evidence_score = (
        state.get(
            "evidence_score"
        )
    )


    evidence_sufficient = (
        state.get(
            "evidence_sufficient"
        )
    )


    evidence_gaps = (
        state.get(
            "evidence_gaps"
        )
        or []
    )


    evidence_evaluated = (
        evidence_score
        is not None
        or
        evidence_sufficient
        is not None
        or
        bool(
            evidence_gaps
        )
    )


    evidence = (
        EvidenceResponse(
            evaluated=(
                evidence_evaluated
            ),

            sufficient=(
                evidence_sufficient
            ),

            score=(
                evidence_score
            ),

            gaps=[
                str(item)
                for item
                in evidence_gaps
            ],
        )
    )


    # ========================================================
    # Retry Queries
    # ========================================================

    raw_retry_queries = (
        state.get(
            "retry_queries"
        )
        or []
    )


    retry_queries: list[
        RetryQueryResponse
    ] = []


    for item in (
        raw_retry_queries
    ):
        if isinstance(
            item,
            dict,
        ):
            retry_queries.append(
                RetryQueryResponse(
                    company=str(
                        item.get(
                            "company",
                            "",
                        )
                    ),

                    query=str(
                        item.get(
                            "query",
                            "",
                        )
                    ),

                    gap=str(
                        item.get(
                            "gap",
                            "",
                        )
                    ),
                )
            )

        else:
            retry_queries.append(
                RetryQueryResponse(
                    query=str(
                        item
                    )
                )
            )


    retry = (
        RetryResponse(
            count=int(
                state.get(
                    "retry_count",
                    0,
                )
                or 0
            ),

            queries=(
                retry_queries
            ),

            reason=str(
                state.get(
                    "retry_reason",
                    "",
                )
                or ""
            ),
        )
    )


    # ========================================================
    # Evidence Tracking
    # ========================================================

    evidence_ids = (
        state.get(
            "evidence_ids"
        )
        or []
    )


    tracking = (
        EvidenceTrackingResponse(
            unique=len(
                evidence_ids
            ),

            new=int(
                state.get(
                    "new_evidence_count",
                    0,
                )
                or 0
            ),

            duplicates=int(
                state.get(
                    "duplicate_evidence_count",
                    0,
                )
                or 0
            ),

            last_new=int(
                state.get(
                    "last_new_evidence_count",
                    0,
                )
                or 0
            ),

            last_duplicates=int(
                state.get(
                    "last_duplicate_evidence_count",
                    0,
                )
                or 0
            ),
        )
    )


    # ========================================================
    # Tool Trace
    # ========================================================

    tool_trace = (
        collect_tool_trace(
            state.get(
                "messages"
            )
            or []
        )
    )


    # ========================================================
    # Final Response
    # ========================================================

    return ResearchResponse(
        query=query,

        task_type=(
            state.get(
                "task_type"
            )
        ),

        complexity=(
            state.get(
                "complexity"
            )
        ),

        plan=plan,

        answer=str(
            state.get(
                "answer",
                "",
            )
            or ""
        ),

        tool_trace=(
            tool_trace
        ),

        tool_rounds=int(
            state.get(
                "tool_rounds",
                0,
            )
            or 0
        ),

        evidence=(
            evidence
        ),

        retry=(
            retry
        ),

        evidence_tracking=(
            tracking
        ),

        token_usage=(
            token_usage
        ),

        timing=(
            timing
        ),
    )


# ============================================================
# Research API
# ============================================================


@app.post(
    "/api/research",

    response_model=(
        ResearchResponse
    ),
)
async def research(
    request: ResearchRequest,
):
    query = (
        request.query
        .strip()
    )


    if not query:
        raise HTTPException(
            status_code=400,

            detail=(
                "Query cannot be empty."
            ),
        )


    try:
        (
            result,
            token_usage,
            timing,
        ) = (
            await run_in_threadpool(
                run_research_with_metrics,
                query,
            )
        )


        response = (
            build_response(
                query=query,

                state=result,

                token_usage=(
                    token_usage
                ),

                timing=(
                    timing
                ),
            )
        )


        print(
            "\n"
            "========================================"
        )

        print(
            "[Research Completed]"
        )

        print(
            f"Query: {query}"
        )

        print(
            "Tokens: "
            f"{response.token_usage.total_tokens}"
        )

        print(
            "LLM calls: "
            f"{response.token_usage.llm_calls}"
        )

        print(
            "Execution time: "
            f"{response.timing.total_seconds}s"
        )

        print(
            "========================================"
            "\n"
        )


        return response


    except Exception as exc:
        traceback.print_exc()


        raise HTTPException(
            status_code=500,

            detail=(
                "Research execution failed: "
                + str(exc)
            ),
        ) from exc