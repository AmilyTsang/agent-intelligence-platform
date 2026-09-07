import traceback

from fastapi import (
    FastAPI,
    HTTPException,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.concurrency import (
    run_in_threadpool,
)

from langchain_core.messages import (
    ToolMessage,
)

from app.agent.graph import (
    research_graph,
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


# ============================================================
# FastAPI App
# ============================================================


app = FastAPI(
    title="Agent Intelligence Platform API",
    description=(
        "基于 LangGraph 的企业 AI 产品研究"
        "与决策分析智能体 API"
    ),
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # 如果以后 React 改用其他常见开发端口，
    # 可以直接继续添加。
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# Helpers
# ============================================================


def normalize_plan(
    raw_plan,
) -> list[PlanStepResponse]:
    """
    将 AgentState.plan
    转换成稳定 API Schema。
    """

    if not isinstance(
        raw_plan,
        list,
    ):
        return []

    result = []

    for index, item in enumerate(
        raw_plan,
        start=1,
    ):

        if not isinstance(
            item,
            dict,
        ):
            continue

        step_id = item.get(
            "step_id",
            index,
        )

        try:

            step_id = int(
                step_id
            )

        except Exception:

            step_id = index

        action = str(
            item.get(
                "action",
                "research",
            )
        ).strip()

        description = str(
            item.get(
                "description",
                "",
            )
        ).strip()

        if not description:
            continue

        result.append(
            PlanStepResponse(
                step_id=step_id,
                action=action,
                description=description,
            )
        )

    return result


def normalize_retry_queries(
    raw_queries,
) -> list[RetryQueryResponse]:
    """
    将 Query Rewriter 输出转换成 API Schema。
    """

    if not isinstance(
        raw_queries,
        list,
    ):
        return []

    result = []

    for item in raw_queries:

        if not isinstance(
            item,
            dict,
        ):
            continue

        company = str(
            item.get(
                "company",
                "",
            )
        ).strip()

        query = str(
            item.get(
                "query",
                "",
            )
        ).strip()

        gap = str(
            item.get(
                "gap",
                "",
            )
        ).strip()

        if not company:
            continue

        if not query:
            continue

        result.append(
            RetryQueryResponse(
                company=company,
                query=query,
                gap=gap,
            )
        )

    return result


def extract_tool_trace(
    messages,
) -> list[ToolTraceItem]:
    """
    从 LangGraph MessagesState 中
    获取实际已经执行完成的 Tool。

    为什么使用 ToolMessage：

    Agent 可能提出 tool_call，
    但随后被 Tool Loop Limit 阻止。

    如果直接读取 AIMessage.tool_calls，
    就会把“提出过”误认为“执行过”。

    ToolMessage 才代表 Tool 已经真正返回结果。
    """

    if not isinstance(
        messages,
        list,
    ):
        return []

    trace = []

    index = 1

    for message in messages:

        if not isinstance(
            message,
            ToolMessage,
        ):
            continue

        tool_name = getattr(
            message,
            "name",
            None,
        )

        if not tool_name:
            tool_name = "unknown"

        trace.append(
            ToolTraceItem(
                index=index,
                name=str(
                    tool_name
                ),
            )
        )

        index += 1

    return trace


def build_response(
    query: str,
    state: dict,
) -> ResearchResponse:
    """
    将内部 AgentState 转换成
    对外稳定 ResearchResponse。

    前端以后不应该直接读取 AgentState，
    而应该始终读取这一层。
    """

    # ========================================================
    # Evidence
    # ========================================================

    evidence_evaluated = (
        "evidence_sufficient"
        in state
    )

    evidence = EvidenceResponse(
        evaluated=evidence_evaluated,

        sufficient=state.get(
            "evidence_sufficient"
        ),

        score=state.get(
            "evidence_score"
        ),

        gaps=state.get(
            "evidence_gaps",
            [],
        )
        or [],
    )

    # ========================================================
    # Retry
    # ========================================================

    retry = RetryResponse(
        count=state.get(
            "retry_count",
            0,
        ),

        queries=normalize_retry_queries(
            state.get(
                "retry_queries",
                [],
            )
        ),

        reason=str(
            state.get(
                "retry_reason",
                "",
            )
            or ""
        ),
    )

    # ========================================================
    # Evidence Tracking
    # ========================================================

    evidence_ids = state.get(
        "evidence_ids",
        [],
    )

    if not isinstance(
        evidence_ids,
        list,
    ):
        evidence_ids = []

    tracking = (
        EvidenceTrackingResponse(
            unique=len(
                evidence_ids
            ),

            new=state.get(
                "new_evidence_count",
                0,
            ),

            duplicates=state.get(
                "duplicate_evidence_count",
                0,
            ),

            last_new=state.get(
                "last_new_evidence_count",
                0,
            ),

            last_duplicates=state.get(
                "last_duplicate_evidence_count",
                0,
            ),
        )
    )

    # ========================================================
    # Response
    # ========================================================

    return ResearchResponse(
        query=query,

        task_type=state.get(
            "task_type"
        ),

        complexity=state.get(
            "complexity"
        ),

        plan=normalize_plan(
            state.get(
                "plan",
                [],
            )
        ),

        answer=str(
            state.get(
                "answer",
                "",
            )
            or ""
        ),

        tool_trace=extract_tool_trace(
            state.get(
                "messages",
                [],
            )
        ),

        tool_rounds=state.get(
            "tool_rounds",
            0,
        ),

        evidence=evidence,

        retry=retry,

        evidence_tracking=tracking,
    )


# ============================================================
# Graph Runner
# ============================================================


def run_research_graph(
    query: str,
):
    """
    同步执行 LangGraph。

    FastAPI endpoint 会通过
    run_in_threadpool 调用这个函数，
    避免长时间 research_graph.invoke()
    阻塞 FastAPI event loop。
    """

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

    return research_graph.invoke(
        initial_state
    )


# ============================================================
# Routes
# ============================================================


@app.get("/")
def root():
    """
    基础 API 信息。
    """

    return {
        "name":
            "Agent Intelligence Platform",

        "status":
            "running",

        "docs":
            "/docs",

        "research_endpoint":
            "/api/research",
    }


@app.get("/api/health")
def health():
    """
    健康检查。

    不执行 LLM / RAG，
    所以可以快速判断 API Server
    是否成功启动。
    """

    return {
        "status": "ok"
    }


@app.post(
    "/api/research",
    response_model=ResearchResponse,
)
async def research(
    request: ResearchRequest,
):
    """
    执行完整 Research Agent。

    Flow:

        HTTP Request
        ↓
        FastAPI
        ↓
        LangGraph
        ↓
        Router
        ↓
        RAG / Planner
        ↓
        Tool Calling
        ↓
        Evidence Checker
        ↓
        Evidence-driven Retry
        ↓
        API Response
    """

    query = (
        request.query
        .strip()
    )

    if not query:

        raise HTTPException(
            status_code=400,
            detail=(
                "query cannot be empty"
            ),
        )

    print(
        "\n"
        "========================================"
    )

    print(
        "[API] Research Request"
    )

    print(
        "========================================"
    )

    print(
        f"\nQuery: {query}"
    )

    try:

        # LangGraph 当前为同步调用。
        #
        # Research 可能执行几十秒甚至更久，
        # 所以放到 threadpool 中运行，
        # 避免阻塞 FastAPI asyncio event loop。
        state = await run_in_threadpool(
            run_research_graph,
            query,
        )

    except Exception as exc:

        print(
            "\n[API] Research failed"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Research Agent execution failed."
            ),
        ) from exc

    response = build_response(
        query=query,
        state=state,
    )

    print(
        "\n[API] Research completed"
    )

    print(
        f"task_type="
        f"{response.task_type}"
    )

    print(
        f"complexity="
        f"{response.complexity}"
    )

    print(
        f"retry_count="
        f"{response.retry.count}"
    )

    print(
        f"evidence_score="
        f"{response.evidence.score}"
    )

    return response