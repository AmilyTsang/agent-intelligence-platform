import json

from langchain_core.messages import (
    HumanMessage,
)

from app.agent.state import AgentState


def prepare_retry_node(
    state: AgentState,
):
    """
    将 Query Rewriter 生成的 retry_queries
    转换为下一轮 Agent Research Instruction。

    同时：

    retry_count += 1

    并重置：

    tool_rounds = 0

    让每一轮 Retry 拥有独立 Tool Loop Budget。
    """

    retry_queries = state.get(
        "retry_queries",
        [],
    )

    evidence_gaps = state.get(
        "evidence_gaps",
        [],
    )

    current_retry_count = state.get(
        "retry_count",
        0,
    )

    next_retry_count = (
        current_retry_count + 1
    )

    # ======================================
    # Format Retry Queries
    # ======================================

    retry_query_text = json.dumps(
        retry_queries,
        ensure_ascii=False,
        indent=2,
    )

    gaps_text = json.dumps(
        evidence_gaps,
        ensure_ascii=False,
        indent=2,
    )

    # ======================================
    # Retry Instruction
    # ======================================

    retry_instruction = f"""
这是 Evidence-driven Retry 第 {next_retry_count} 轮。

上一轮 Evidence Checker 判断：

当前证据不足以完整支持研究任务。

请不要从头重复整个研究过程。

你的任务是：

仅针对当前 Evidence Gaps
执行补充研究。


========================
Evidence Gaps
========================

{gaps_text}


========================
Recommended Retry Queries
========================

{retry_query_text}


========================
执行要求
========================

1. 优先按照 Recommended Retry Queries
   调用 company_search。

2. 不要重复搜索已经获得充分证据的内容。

3. 新 Evidence 应用于补充现有研究，
   不要丢弃之前已经获得的 Tool Results。

4. 如有必要，可以继续调用：

   extract_company_info

   compare_companies

   对新 Evidence 进行结构化提取和比较。

5. 当前检索没有发现某项内容，
   不代表该公司不存在该能力。

6. 当新增 Evidence 已足以回答问题时，
   停止 Tool Calling。

7. 最终回答必须综合：

   原有 Evidence
   +
   新增 Evidence

8. 对仍然没有证据支持的维度，
   明确写“当前 Evidence 不足”。

请现在开始执行针对性的补充研究。
"""

    print(
        "\n[Prepare Retry]"
    )

    print(
        f"retry_count: "
        f"{current_retry_count} "
        f"→ {next_retry_count}"
    )

    print(
        f"retry_queries="
        f"{len(retry_queries)}"
    )

    return {
        "messages": [
            HumanMessage(
                content=retry_instruction
            )
        ],

        "retry_count":
            next_retry_count,

        # 每轮 Retry 重新给 Agent
        # 一份 Tool Loop Budget
        "tool_rounds":
            0,
    }