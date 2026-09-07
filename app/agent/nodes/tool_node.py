from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

from app.agent.state import AgentState
from app.agent.nodes.evidence_dedup import (
    filter_new_evidence,
)
from app.tools import tools


# ============================================================
# Tool Registry
# ============================================================


TOOLS_BY_NAME = {
    tool.name: tool
    for tool in tools
}


# ============================================================
# Execute Single Tool
# ============================================================


def execute_tool_call(
    tool_call: dict,
) -> ToolMessage:
    """
    执行单个 Structured Tool Call。

    输入示例：

    {
        "name": "company_search",
        "args": {
            "company": "OpenAI",
            "query": "Agent tools security"
        },
        "id": "call_xxx",
        "type": "tool_call"
    }

    无论 Tool 成功还是失败，
    都返回对应 tool_call_id 的 ToolMessage。

    这样可以确保：

        AIMessage(tool_calls)
        ↓
        ToolMessage(tool_call_id=...)

    始终满足 OpenAI-compatible
    Tool Calling 消息协议。
    """

    tool_name = str(
        tool_call.get(
            "name",
            "",
        )
    ).strip()

    tool_args = tool_call.get(
        "args",
        {},
    )

    tool_call_id = str(
        tool_call.get(
            "id",
            "",
        )
    ).strip()

    # ========================================================
    # Unknown Tool
    # ========================================================

    if tool_name not in TOOLS_BY_NAME:

        error_message = (
            f"Tool execution failed: "
            f"unknown tool '{tool_name}'."
        )

        print(
            "\n[Tool Node]"
        )

        print(
            error_message
        )

        return ToolMessage(
            content=error_message,
            tool_call_id=tool_call_id,
            name=tool_name,
        )

    tool = TOOLS_BY_NAME[
        tool_name
    ]

    # ========================================================
    # Execute
    # ========================================================

    print(
        "\n[Tool Node]"
    )

    print(
        f"Executing: {tool_name}"
    )

    try:

        result = tool.invoke(
            tool_args
        )

        # Tool 一般返回 str，
        # 但这里做兼容处理。
        if isinstance(
            result,
            str,
        ):
            content = result

        else:
            content = str(
                result
            )

        print(
            f"[Tool Node] "
            f"{tool_name} completed"
        )

        return ToolMessage(
            content=content,
            tool_call_id=tool_call_id,
            name=tool_name,
        )

    except Exception as exc:

        error_message = (
            f"Tool execution failed "
            f"for {tool_name}: "
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            f"[Tool Node] "
            f"{error_message}"
        )

        # 非常重要：
        #
        # 即使 Tool 运行失败，
        # 也必须生成 ToolMessage，
        # 回应对应 tool_call_id。
        #
        # 否则下一次调用 LLM 时，
        # 又会出现：
        #
        # assistant tool_calls must be
        # followed by tool messages
        return ToolMessage(
            content=error_message,
            tool_call_id=tool_call_id,
            name=tool_name,
        )


# ============================================================
# Tool Node
# ============================================================


def tool_node(
    state: AgentState,
):
    """
    执行 Agent 最近一次产生的 Structured Tool Calls。

    同时针对 company_search：

        1. 提取 Evidence ID
        2. 与历史 Evidence IDs 比较
        3. 删除重复 Evidence
        4. 只把新增 Evidence 返回给 Agent
        5. 更新 Evidence Tracking State

    不再嵌套调用 LangGraph ToolNode，
    避免部分 LangGraph 版本中的：

        Missing required config key
        'N/A' for 'tools'

    问题。
    """

    messages = state.get(
        "messages",
        [],
    )

    # ========================================================
    # Validate Messages
    # ========================================================

    if not messages:

        print(
            "\n[Tool Node] "
            "No messages found."
        )

        return {
            "messages": [],
            "last_new_evidence_count": 0,
            "last_duplicate_evidence_count": 0,
        }

    last_message = messages[-1]

    # ========================================================
    # Validate AIMessage
    # ========================================================

    if not isinstance(
        last_message,
        AIMessage,
    ):

        print(
            "\n[Tool Node] "
            "Last message is not AIMessage."
        )

        return {
            "messages": [],
            "last_new_evidence_count": 0,
            "last_duplicate_evidence_count": 0,
        }

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None,
    )

    if not tool_calls:

        print(
            "\n[Tool Node] "
            "No tool calls found."
        )

        return {
            "messages": [],
            "last_new_evidence_count": 0,
            "last_duplicate_evidence_count": 0,
        }

    print(
        "\n[Tool Node]"
    )

    print(
        f"Tool calls="
        f"{len(tool_calls)}"
    )

    # ========================================================
    # Execute All Tool Calls
    # ========================================================

    raw_tool_messages = []

    for tool_call in tool_calls:

        tool_message = (
            execute_tool_call(
                tool_call
            )
        )

        raw_tool_messages.append(
            tool_message
        )

    # ========================================================
    # Existing Evidence IDs
    # ========================================================

    previous_ids = state.get(
        "evidence_ids",
        [],
    )

    # 保持原始顺序
    updated_ids = list(
        previous_ids
    )

    seen_ids = set(
        previous_ids
    )

    # ========================================================
    # Evidence Counters
    # ========================================================

    batch_new_ids = []

    batch_duplicate_ids = []

    filtered_messages = []

    # ========================================================
    # Evidence Filtering
    # ========================================================

    for message in raw_tool_messages:

        tool_name = getattr(
            message,
            "name",
            None,
        )

        # ----------------------------------------------------
        # 非 company_search 工具
        #
        # extract / compare 等结果不是原始 Evidence Chunk，
        # 不做 evidence_id 去重。
        # ----------------------------------------------------

        if tool_name != "company_search":

            filtered_messages.append(
                message
            )

            continue

        content = (
            message.content
            if isinstance(
                message.content,
                str,
            )
            else str(
                message.content
            )
        )

        (
            filtered_content,
            new_ids,
            duplicate_ids,
        ) = filter_new_evidence(
            content=content,
            seen_evidence_ids=seen_ids,
        )

        # ====================================================
        # Record New IDs
        # ====================================================

        for evidence_id in new_ids:

            if (
                evidence_id
                not in updated_ids
            ):

                updated_ids.append(
                    evidence_id
                )

        batch_new_ids.extend(
            new_ids
        )

        batch_duplicate_ids.extend(
            duplicate_ids
        )

        # ====================================================
        # Preserve Tool Protocol
        # ====================================================

        filtered_message = (
            message.model_copy(
                update={
                    "content":
                        filtered_content
                }
            )
        )

        filtered_messages.append(
            filtered_message
        )

    # ========================================================
    # Counters
    # ========================================================

    previous_new_count = state.get(
        "new_evidence_count",
        0,
    )

    previous_duplicate_count = state.get(
        "duplicate_evidence_count",
        0,
    )

    batch_new_count = len(
        batch_new_ids
    )

    batch_duplicate_count = len(
        batch_duplicate_ids
    )

    # ========================================================
    # Logging
    # ========================================================

    print(
        "\n[Evidence Dedup]"
    )

    print(
        f"retrieved="
        f"{batch_new_count + batch_duplicate_count}"
    )

    print(
        f"new="
        f"{batch_new_count}"
    )

    print(
        f"duplicates="
        f"{batch_duplicate_count}"
    )

    print(
        f"total_unique_evidence="
        f"{len(updated_ids)}"
    )

    # ========================================================
    # State Update
    # ========================================================

    return {
        "messages":
            filtered_messages,

        "evidence_ids":
            updated_ids,

        "new_evidence_count":
            previous_new_count
            + batch_new_count,

        "duplicate_evidence_count":
            previous_duplicate_count
            + batch_duplicate_count,

        "last_new_evidence_count":
            batch_new_count,

        "last_duplicate_evidence_count":
            batch_duplicate_count,
    }