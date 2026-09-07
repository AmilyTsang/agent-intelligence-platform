import json

from pydantic import (
    BaseModel,
    Field,
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
# Structured Output
# ============================================================


class RetryQuery(BaseModel):
    """
    单条补充检索 Query。
    """

    company: str = Field(
        description=(
            "需要补充检索的公司名称，"
            "例如 OpenAI、Google"
        )
    )

    query: str = Field(
        description=(
            "用于企业知识库向量检索的精准查询"
        )
    )

    gap: str = Field(
        description=(
            "该查询试图补充解决的 Evidence Gap"
        )
    )


class QueryRewriteResult(BaseModel):
    """
    Query Rewriter 输出。
    """

    retry_queries: list[RetryQuery] = Field(
        default_factory=list,
        description=(
            "根据 Evidence Gaps 生成的补充检索任务"
        ),
    )

    reason: str = Field(
        description=(
            "本轮 Query Rewrite 策略说明"
        )
    )


# ============================================================
# Prompt
# ============================================================


QUERY_REWRITE_PROMPT = """
你是 Agent Intelligence Platform 的 Query Rewriter。

当前 Research Agent 已经完成了一轮研究，
Evidence Checker 判断当前证据仍存在缺口。

你的任务不是重新回答用户问题。

你的任务是：

根据 Evidence Gaps，
生成下一轮更加精准的企业知识库检索 Query。


==================================================
用户原始问题
==================================================

{query}


==================================================
Research Plan
==================================================

{plan}


==================================================
Evidence Gaps
==================================================

{evidence_gaps}


==================================================
Query Rewrite 目标
==================================================

新的 Query 必须针对 Evidence Gap。

不要简单重复用户原始问题。

例如原问题：

“比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异。”

Evidence Gap：

“当前已检索的 OpenAI Evidence
未覆盖工具安全与权限管理。”

错误 Query：

“OpenAI Agent Tools”

这个 Query 太宽泛。


更好的 Query：

“Agent Tools guardrails permissions security
tool authorization safety”

因为它直接针对缺失维度。


==================================================
公司拆分规则
==================================================

如果 Evidence Gap 涉及不同公司，

应该分别生成 Query。


例如：

Gap 1：

当前 OpenAI Evidence
未覆盖工具安全与权限控制。


Gap 2：

当前 Google Evidence
未覆盖工具错误处理机制。


应该生成：

OpenAI:
Agent Tools guardrails permissions
tool security authorization


Google:
ADK tool error handling ToolContext
tool failure exception handling


不要把两个公司的 Query
强行合并成一条。


==================================================
双边 Evidence Gap
==================================================

如果某个 Evidence Gap 同时涉及双方，

例如：

“当前双方 Evidence
均缺少工具调用性能指标。”

可以分别为两家公司生成 Query：

OpenAI:
Agent Tools tool calling latency
performance benchmark cost success rate

Google:
ADK tool calling latency
performance benchmark cost success rate


==================================================
检索 Query 设计原则
==================================================

每条 Query 应该：

1. 简洁
2. 聚焦
3. 包含核心技术关键词
4. 针对具体 Evidence Gap
5. 适合向量检索
6. 不写成长篇自然语言问题


推荐形式：

核心主题
+
技术概念
+
同义词 / 相关术语


例如：

Agent Tools security permission
authorization guardrails tool safety


而不是：

“请告诉我 OpenAI 的 Agent Tools
是如何进行安全权限管理的？”


==================================================
重要约束
==================================================

1. Evidence Gap 不是企业事实。

例如：

“当前 Evidence 未覆盖 OpenAI MCP”

不代表：

“OpenAI 不支持 MCP”。


2. 不允许使用模型自身知识
假设某家公司一定存在某个功能。


3. Query 可以寻找某个能力是否被文档覆盖，

但不能预设结论。


正确：

“OpenAI Agent MCP interoperability
tool protocol integration”


错误：

“OpenAI MCP implementation details”

如果当前 Evidence 根本没有证明
OpenAI 一定存在该实现。


4. Research Plan 不是 Evidence。


5. Query Rewriter 不负责回答问题。


6. Query Rewriter 不负责判断
Evidence 是否充分。


7. Query Rewriter 只负责：
针对当前 gaps 生成补充检索 Query。


==================================================
Query 数量
==================================================

通常生成：

1 到 4 条 Query。

不要因为存在多个细小 Gap
生成大量重复检索任务。

优先补：

- 会影响主要结论的 Gap
- 企业比较双方不平衡的 Gap
- 用户问题核心维度的 Gap


==================================================
输出
==================================================

必须输出合法 JSON。

不得输出 Markdown。

不得输出额外解释。

{format_instructions}
"""


# ============================================================
# Query Rewriter Node
# ============================================================


def query_rewriter_node(
    state: AgentState,
):
    """
    根据 Evidence Checker 生成的 Evidence Gaps，
    创建下一轮补充研究 Query。

    输入：

        query
        plan
        evidence_gaps

    输出：

        retry_queries
        retry_reason

    当前节点不执行 Search。
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
    # Evidence Gaps
    # ========================================================

    evidence_gaps = state.get(
        "evidence_gaps",
        [],
    )

    # ========================================================
    # No Gaps
    # ========================================================

    if not evidence_gaps:

        print(
            "\n[Query Rewriter]"
        )

        print(
            "No Evidence Gaps "
            "→ No Retry Query"
        )

        return {
            "retry_queries": [],
            "retry_reason": (
                "当前没有 Evidence Gap，"
                "无需生成补充检索 Query。"
            ),
        }

    # ========================================================
    # Format Input
    # ========================================================

    plan_text = json.dumps(
        plan,
        ensure_ascii=False,
        indent=2,
    )

    gaps_text = json.dumps(
        evidence_gaps,
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
        pydantic_object=QueryRewriteResult
    )

    # ========================================================
    # Prompt
    # ========================================================

    prompt = (
        ChatPromptTemplate.from_template(
            QUERY_REWRITE_PROMPT
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
            "evidence_gaps":
                gaps_text,
            "format_instructions":
                parser.get_format_instructions(),
        }
    )

    # ========================================================
    # Normalize
    # ========================================================

    raw_queries = result.get(
        "retry_queries",
        [],
    )

    retry_queries = []

    if isinstance(
        raw_queries,
        list,
    ):

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

            rewritten_query = str(
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

            if (
                company
                and rewritten_query
            ):

                retry_queries.append(
                    {
                        "company": company,
                        "query":
                            rewritten_query,
                        "gap": gap,
                    }
                )

    # 最多保留 4 条
    retry_queries = (
        retry_queries[:4]
    )

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
        "\n[Query Rewriter]"
    )

    if retry_queries:

        print(
            f"Generated "
            f"{len(retry_queries)} "
            f"retry queries:"
        )

        for index, item in enumerate(
            retry_queries,
            start=1,
        ):

            print(
                f"\n  Query {index}"
            )

            print(
                f"  Company: "
                f"{item['company']}"
            )

            print(
                f"  Query: "
                f"{item['query']}"
            )

            print(
                f"  Gap: "
                f"{item['gap']}"
            )

    else:

        print(
            "No valid retry query generated."
        )

    if reason:

        print(
            f"\nReason: {reason}"
        )

    # ========================================================
    # State Update
    # ========================================================

    return {
        "retry_queries":
            retry_queries,

        "retry_reason":
            reason,
    }