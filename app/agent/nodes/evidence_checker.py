import json
from typing import Any

from pydantic import BaseModel, Field

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from langchain_core.output_parsers import (
    JsonOutputParser,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
)

from app.agent.state import AgentState
from app.services.llm import get_llm


# ============================================================
# Evidence Checker Structured Output
# ============================================================


class EvidenceCheckResult(BaseModel):
    """
    Evidence Checker 的结构化输出 Schema。
    """

    sufficient: bool = Field(
        description=(
            "当前已获得 Evidence 是否足以支持用户问题的主要结论"
        )
    )

    score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Evidence 的整体充分程度，取值范围 0~1"
        ),
    )

    gaps: list[str] = Field(
        default_factory=list,
        description=(
            "当前 Research Run 中仍缺失的重要 Evidence"
        ),
    )

    reason: str = Field(
        description=(
            "Evidence 是否充分的简短判断理由"
        ),
    )


# ============================================================
# Evidence Checker Prompt
# ============================================================


EVIDENCE_CHECK_PROMPT = """
你是 Agent Intelligence Platform 的 Evidence Checker。

你的职责不是继续研究，也不是生成新的企业事实。

你的唯一任务是：

判断当前 Research Run 已经获得的 Tool Evidence，
是否足以支持用户原始问题以及当前候选答案中的主要结论。


==================================================
用户原始问题
==================================================

{query}


==================================================
Research Plan
==================================================

{plan}


==================================================
已经成功执行完成的 Tool Results
==================================================

{tool_results}


==================================================
当前候选答案
==================================================

{candidate_answer}


==================================================
评估维度
==================================================

请从以下四个核心维度评估当前 Evidence。


1. Coverage

判断用户问题中的核心研究维度是否已经获得 Evidence。

例如企业 Agent Tools 比较可能涉及：

- 工具定义
- Tool Calling
- Function Calling
- 工具调用机制
- 上下文管理
- 错误处理
- 安全与权限
- 扩展性
- 工具生态
- Agent 编排

Research Plan 中出现某个维度，
不代表该维度已经获得 Evidence。

只检查真正出现在 Tool Results 中的信息。


2. Grounding

检查候选答案中的关键企业事实，
是否能够从 Tool Results 中找到对应支持。

不能因为某个结论听起来合理，
就认为该结论已经被 Evidence 支持。

模型自身知识不是 Evidence。


3. Balance

对于企业对比任务，
检查双方 Evidence 是否足够平衡。

例如：

Company A 对某个维度有大量 Evidence，
但 Company B 没有对应 Evidence，

则不能直接得出强比较结论。

这种情况应该：

- 降低 score
- 在 gaps 中明确记录


4. Missing Information

严格区分：

“当前已检索 Evidence 中没有发现”

和：

“该公司不存在此能力”

这两种表述完全不同。


==================================================
关键语义约束
==================================================

你判断的是：

“当前 Research Run 的 Evidence 是否充分”

而不是：

“整个知识库是否包含某项能力”

更不是：

“某家公司是否具备某项能力”。


禁止根据当前检索结果推断：

- 整份文档没有某项内容
- 整个知识库没有某项内容
- 某家公司没有某项能力


错误表述：

“OpenAI 资料中未涉及 MCP。”

“Google 文档没有 Guardrail。”

“OpenAI 不支持某项能力。”


正确表述：

“当前已检索到的 OpenAI Evidence 未覆盖 MCP 相关内容。”

“当前已检索到的 Google Evidence 未覆盖 Guardrail 相关内容。”

“当前 Evidence 不足以判断 OpenAI 是否支持该能力。”


Evidence Gap 应描述：

“当前检索证据缺什么”

而不是：

“某家公司没有什么”。


==================================================
Research Plan 规则
==================================================

Research Plan 不是 Evidence。

例如 Planner 提到：

- Code Interpreter
- File Search
- MCP
- A2A
- Security
- Guardrails

不代表知识库已经提供这些事实。

只有已经成功执行完成的 Tool Result
才可以作为 Evidence。


==================================================
Tool Call 规则
==================================================

AIMessage 中的 tool_calls 只是：

“Agent 希望调用某个 Tool”

它不代表工具已经执行成功。

只有对应 ToolMessage 真正存在，
才代表 Tool 已经执行完成。

因此：

Tool Call ≠ Tool Result

Tool Result 才属于 Evidence。


==================================================
充分性判断原则
==================================================

不要求所有 Research Plan 步骤全部机械完成。

应该判断：

用户主要问题是否已经可以被可靠回答。


如果：

- 核心结论已有充分 Evidence
- 少量非核心维度仍然缺失

可以：

sufficient = true


如果：

- 用户主要比较维度缺失
- 双方 Evidence 严重不平衡
- 关键结论无法被 Evidence 支持
- 当前资料只能支持非常有限的结论

应该：

sufficient = false


==================================================
Score 参考标准
==================================================

0.00 - 0.39

Evidence 严重不足。

无法可靠回答用户主要问题。


0.40 - 0.69

已有部分有效 Evidence，

但多个核心维度仍存在明显缺口。


0.70 - 0.84

大部分核心结论已经有 Evidence 支持，

但仍存在一些明显 Evidence Gap。


0.85 - 1.00

核心研究维度拥有较完整、
平衡、可追溯的 Evidence。


注意：

score 不是答案质量评分。

score 只评价 Evidence 的充分程度。


==================================================
Gaps 输出要求
==================================================

gaps 必须：

1. 描述具体缺失信息
2. 尽量指出是哪家公司、哪个研究维度
3. 使用“当前 Evidence 未覆盖”这类措辞
4. 不得声称公司不存在某项能力
5. 不要把非核心的小缺口无限放大


例如：

正确：

“当前已检索的 OpenAI Evidence
未覆盖工具权限管理机制，
因此无法与 Google 进行完整比较。”


错误：

“OpenAI 没有权限管理机制。”


==================================================
最终输出
==================================================

必须输出合法 JSON。

不得输出 Markdown。

不得输出额外解释。

{format_instructions}
"""


# ============================================================
# Helper: normalize message content
# ============================================================


def _content_to_text(
    content: Any,
) -> str:
    """
    将 LangChain Message content 转换为普通文本。

    content 在不同模型/SDK 下，
    可能是 str、list、dict 等类型。
    """

    if isinstance(
        content,
        str,
    ):
        return content

    try:
        return json.dumps(
            content,
            ensure_ascii=False,
        )

    except Exception:
        return str(content)


# ============================================================
# Helper: collect completed Tool Results
# ============================================================


def _collect_tool_results(
    state: AgentState,
) -> list[dict]:
    """
    从 MessagesState 中收集已经成功执行完成的 ToolMessage。

    重要：

    AIMessage(tool_calls=[...])
    只表示 Agent 提出了 Tool Call。

    它不属于 Evidence。

    只有 ToolMessage 才代表 Tool 已真正执行。
    """

    results = []

    messages = state.get(
        "messages",
        [],
    )

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
            tool_name = "unknown_tool"

        content = _content_to_text(
            message.content
        )

        tool_call_id = getattr(
            message,
            "tool_call_id",
            None,
        )

        results.append(
            {
                "tool_name": tool_name,
                "tool_call_id": tool_call_id,
                "content": content,
            }
        )

    return results


# ============================================================
# Helper: get candidate final answer
# ============================================================


def _get_candidate_answer(
    state: AgentState,
) -> str:
    """
    获取当前候选最终答案。

    优先使用 state["answer"]。

    如果没有 answer，
    再从 messages 中寻找最近一个：
    - AIMessage
    - 不含 tool_calls
    - content 非空
    """

    state_answer = state.get(
        "answer",
        "",
    )

    if isinstance(
        state_answer,
        str,
    ) and state_answer.strip():

        return state_answer.strip()

    messages = state.get(
        "messages",
        [],
    )

    for message in reversed(
        messages
    ):

        if not isinstance(
            message,
            AIMessage,
        ):
            continue

        tool_calls = getattr(
            message,
            "tool_calls",
            [],
        )

        # 未执行完成的 Tool Call
        # 不能视作最终答案
        if tool_calls:
            continue

        content = _content_to_text(
            message.content
        )

        if content.strip():
            return content.strip()

    return ""


# ============================================================
# Helper: format Tool Evidence
# ============================================================


def _format_tool_results(
    results: list[dict],
) -> str:
    """
    将 Tool Results 格式化为 Evidence Checker Context。

    当前阶段采用简单字符截断控制 Context 大小。

    后续 Context Engineering 阶段
    再升级为：
    - rerank
    - dedup
    - source diversity
    - token budget
    """

    if not results:

        return (
            "当前没有已经成功执行完成的 Tool Result。"
        )

    parts = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        content = result.get(
            "content",
            "",
        )

        # 避免单条 Tool Result 过大
        if len(content) > 6000:

            content = (
                content[:6000]
                + "\n...[truncated]"
            )

        tool_name = result.get(
            "tool_name",
            "unknown_tool",
        )

        parts.append(
            (
                f"===== Tool Result {index} =====\n"
                f"Tool: {tool_name}\n\n"
                f"{content}"
            )
        )

    return "\n\n".join(
        parts
    )


# ============================================================
# Evidence Checker Node
# ============================================================


def evidence_checker_node(
    state: AgentState,
):
    """
    LangGraph Evidence Checker Node。

    输入：

        query
        plan
        messages
        answer

    输出：

        evidence_sufficient
        evidence_score
        evidence_gaps
    """

    # ========================================================
    # Original Query
    # ========================================================

    query = state.get(
        "query",
        "",
    )

    # ========================================================
    # Research Plan
    # ========================================================

    plan = state.get(
        "plan",
        [],
    )

    # ========================================================
    # Collect completed Evidence
    # ========================================================

    tool_results = (
        _collect_tool_results(
            state
        )
    )

    # ========================================================
    # No Tool Evidence
    # ========================================================

    if not tool_results:

        print(
            "\n[Evidence Checker]"
        )

        print(
            "sufficient=False"
        )

        print(
            "score=0.00"
        )

        print(
            "Evidence Gaps:"
        )

        print(
            "  1. 当前没有已经成功执行完成的 Tool Evidence"
        )

        return {
            "evidence_sufficient": False,
            "evidence_score": 0.0,
            "evidence_gaps": [
                (
                    "当前没有已经成功执行完成的 "
                    "Tool Evidence"
                )
            ],
        }

    # ========================================================
    # Candidate Answer
    # ========================================================

    candidate_answer = (
        _get_candidate_answer(
            state
        )
    )

    if not candidate_answer:

        candidate_answer = (
            "当前尚未生成候选最终答案。"
        )

    # ========================================================
    # Context Formatting
    # ========================================================

    tool_context = (
        _format_tool_results(
            tool_results
        )
    )

    plan_text = json.dumps(
        plan,
        ensure_ascii=False,
        indent=2,
    )

    # ========================================================
    # LLM
    # ========================================================

    llm = get_llm(
        temperature=0
    )

    # ========================================================
    # Parser
    # ========================================================

    parser = JsonOutputParser(
        pydantic_object=EvidenceCheckResult
    )

    # ========================================================
    # Prompt
    # ========================================================

    prompt = (
        ChatPromptTemplate.from_template(
            EVIDENCE_CHECK_PROMPT
        )
    )

    # ========================================================
    # Chain
    # ========================================================

    chain = (
        prompt
        |
        llm
        |
        parser
    )

    # ========================================================
    # Execute
    # ========================================================

    result = chain.invoke(
        {
            "query": query,
            "plan": plan_text,
            "tool_results": tool_context,
            "candidate_answer":
                candidate_answer,
            "format_instructions":
                parser.get_format_instructions(),
        }
    )

    # ========================================================
    # Normalize: sufficient
    # ========================================================

    sufficient = bool(
        result.get(
            "sufficient",
            False,
        )
    )

    # ========================================================
    # Normalize: score
    # ========================================================

    try:

        score = float(
            result.get(
                "score",
                0.0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        score = 0.0

    score = max(
        0.0,
        min(
            1.0,
            score,
        ),
    )

    # ========================================================
    # Normalize: gaps
    # ========================================================

    gaps = result.get(
        "gaps",
        [],
    )

    if not isinstance(
        gaps,
        list,
    ):

        gaps = [
            str(gaps)
        ]

    gaps = [
        str(gap).strip()
        for gap in gaps
        if str(gap).strip()
    ]

    # ========================================================
    # Normalize: reason
    # ========================================================

    reason = str(
        result.get(
            "reason",
            "",
        )
    ).strip()

    # ========================================================
    # Logging
    # ========================================================

    print(
        "\n[Evidence Checker]"
    )

    print(
        f"sufficient={sufficient}"
    )

    print(
        f"score={score:.2f}"
    )

    if gaps:

        print(
            "Evidence Gaps:"
        )

        for index, gap in enumerate(
            gaps,
            start=1,
        ):

            print(
                f"  {index}. {gap}"
            )

    else:

        print(
            "Evidence Gaps: None"
        )

    if reason:

        print(
            f"Reason: {reason}"
        )

    # ========================================================
    # State Update
    # ========================================================

    return {
        "evidence_sufficient":
            sufficient,

        "evidence_score":
            score,

        "evidence_gaps":
            gaps,
    }