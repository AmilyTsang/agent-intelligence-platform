import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.agent.state import AgentState
from app.services.llm import get_llm


FORCE_FINALIZE_PROMPT = """
你是 Agent Intelligence Platform 的最终报告生成节点。

当前 Agent 已经达到最大 Tool Calling 轮数。

因此：

禁止继续调用任何工具。

你的任务是根据“已经成功执行完成”的 Tool Result，
生成当前证据能够支持的最佳最终答案。


要求：

1. 只能使用已经成功获得的 Tool Result。
2. 不得使用尚未执行的 Tool Call。
3. 不得使用模型自身记忆补充企业事实。
4. 如果证据不足，明确说明“当前资料不足”。
5. 不得因为任务没有完全完成而编造内容。
6. 尽可能保留 Source、Page 等证据信息。
7. 明确区分：
   - 文档事实
   - 分析判断
8. 直接输出最终结果。
9. 不要描述内部执行过程。
10. 不要说：
   - “我达到了最大工具次数”
   - “我无法继续调用工具”
   - “让我继续分析”
"""


def force_finalize_node(
    state: AgentState,
):
    """
    Tool Loop 达到上限后的安全结束节点。

    重要：
    不直接复用原始 MessagesState。

    因为最后一个 AIMessage 可能包含
    尚未执行的 tool_calls。

    OpenAI-compatible API 要求：
        AIMessage(tool_calls)
        必须紧跟对应 ToolMessage。

    因此这里仅收集已经执行完成的 ToolMessage，
    将其转换为普通文本 Context 后重新调用 LLM。
    """

    print(
        "\n[Agent] Force Finalize "
        "→ Tool round limit reached"
    )

    llm = get_llm(
        temperature=0
    )

    # ========================
    # Original Query
    # ========================

    query = state.get(
        "query",
        "",
    )

    # ========================
    # Research Plan
    # ========================

    plan = state.get(
        "plan",
        [],
    )

    # ========================
    # Collect completed tools
    # ========================

    completed_tool_results = []

    messages = state.get(
        "messages",
        [],
    )

    for index, message in enumerate(
        messages,
        start=1,
    ):

        # 只接受已经真正执行完成的 ToolMessage
        if isinstance(
            message,
            ToolMessage,
        ):

            tool_name = getattr(
                message,
                "name",
                "unknown_tool",
            )

            content = message.content

            completed_tool_results.append(
                {
                    "tool_name": tool_name,
                    "content": content,
                }
            )

    # ========================
    # Build safe context
    # ========================

    if completed_tool_results:

        tool_context_parts = []

        for index, result in enumerate(
            completed_tool_results,
            start=1,
        ):

            tool_context_parts.append(
                (
                    f"===== Completed Tool Result "
                    f"{index} =====\n"
                    f"Tool: {result['tool_name']}\n\n"
                    f"{result['content']}"
                )
            )

        tool_context = "\n\n".join(
            tool_context_parts
        )

    else:

        tool_context = (
            "当前没有已经成功完成的 Tool Result。"
        )

    # ========================
    # Finalization Input
    # ========================

    finalization_request = f"""
用户原始问题：

{query}


Research Plan：

{json.dumps(
    plan,
    ensure_ascii=False,
    indent=2,
)}


已经成功执行完成的 Tool Result：

{tool_context}


请根据以上已经完成的证据，
生成当前能够支持的最终答案。

如果原计划中还有步骤没有完成，
不要假装已经完成。

对于无法由当前 Tool Result 支持的部分，
明确说明资料不足。
"""

    # ========================
    # IMPORTANT
    # ========================
    #
    # 这里不使用：
    #
    # *state["messages"]
    #
    # 也不使用 ToolMessage 原始角色。
    #
    # 而是把已完成工具结果转换为普通文本，
    # 避免 unmatched tool_call_id。
    # ========================

    response = llm.invoke(
        [
            SystemMessage(
                content=FORCE_FINALIZE_PROMPT
            ),
            HumanMessage(
                content=finalization_request
            ),
        ]
    )

    print(
        "[Agent] Force Finalize "
        "→ Final Answer generated"
    )

    return {
        "messages": [
            response
        ],
        "answer": response.content,
    }