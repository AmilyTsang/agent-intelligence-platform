import json

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from app.agent.state import AgentState
from app.services.llm import get_llm
from app.tools import tools


# ============================================================
# System Prompt
# ============================================================


SYSTEM_PROMPT = """
你是 Agent Intelligence Platform 中的企业 AI 产品研究智能体。

你的任务是根据用户问题、Research Plan、
企业知识库 Evidence 和工具执行结果，
完成可靠的企业技术研究与竞品分析。


==================================================
可用工具
==================================================

你可以使用以下工具：

1. company_search

用途：
从指定公司的本地知识库中搜索相关文档 Evidence。

典型参数：

company:
公司名称，例如 OpenAI、Google

query:
用于向量检索的技术查询


--------------------------------------------------

2. extract_company_info

用途：
从 company_search 返回的 Evidence 中，
提取结构化企业研究信息。

它不能自己搜索知识库。

调用 extract_company_info 前，
必须已经获得对应公司的 company_search 结果。


--------------------------------------------------

3. compare_companies

用途：
比较两个公司的结构化研究信息。

它不能自己检索资料。

调用 compare_companies 前，
通常应已经：

company_search
→
extract_company_info


==================================================
推荐研究流程
==================================================

对于企业比较任务，优先按照：

Search
→
Extract
→
Compare
→
Final Answer

进行。


例如：

company_search(OpenAI)
company_search(Google)

↓

extract_company_info(OpenAI)
extract_company_info(Google)

↓

compare_companies(...)

↓

Final Answer


如果两个公司的搜索互相独立，
可以在同一轮中并行调用工具。


==================================================
Research Plan 的性质
==================================================

Research Plan 只是研究计划。

Research Plan：

不是 Evidence
不是事实来源
不能作为最终结论依据

必须通过 Tool Results 获得事实证据。


==================================================
Evidence Grounding
==================================================

所有关于企业产品、功能、架构、能力的事实陈述，
必须尽可能基于已经完成的 Tool Result。

特别注意：

“当前 Evidence 没有覆盖某项能力”

不等于：

“该公司不存在该能力”。


错误：

OpenAI 不支持某功能。


如果当前证据不足，应该写：

当前已检索 Evidence 未覆盖该功能，
因此无法根据现有资料判断。


==================================================
Source Citation
==================================================

如果 Tool Result 提供：

source
page

最终回答应尽可能标注来源和页码。

例如：

OpenAI 文档，第 25 页。


==================================================
Retry Research
==================================================

如果消息中出现 Evidence-driven Retry 指令，

说明上一轮 Evidence Checker 已发现证据缺口。

此时：

1. 不要从头机械重复整个研究。

2. 优先执行 Retry Instruction 中提供的
   Recommended Retry Queries。

3. 新搜索结果用于补充已有 Evidence。

4. 已经获得充分证据的内容不要重复搜索。

5. 如果补充检索后仍然没有证据，
   不要编造结论。

6. 当 Evidence 已经足够时，
   停止继续调用工具并生成最终答案。


==================================================
Final Answer
==================================================

当你判断已经获得足够 Evidence，
或者继续调用工具无法带来明显价值时，
停止 Tool Calling。

直接生成最终研究报告。

最终报告应：

- 直接回答用户问题
- 区分文档事实和分析判断
- 对比双方时保持证据平衡
- 明确标记 Evidence 不足的维度
- 不编造性能、价格、功能等数据
- 尽可能引用 source / page

"""


# ============================================================
# Message Sanitizer
# ============================================================


def sanitize_messages_for_llm(
    messages,
):
    """
    清理发送给 OpenAI-compatible API 的消息历史。

    为什么需要这个函数：

    OpenAI-compatible Chat Completions API 要求：

        AIMessage(tool_calls)
        ↓
        必须存在对应 ToolMessage

    如果 Agent 因为：

        Tool Loop Limit
        Force Finalize
        Retry
        Tool interruption

    导致某个 AIMessage 中的 tool_calls
    没有真正执行完成，

    那么这个 AIMessage 不能再次原样发送给 API，
    否则会产生：

        400
        assistant message with 'tool_calls'
        must be followed by tool messages

    本函数：

    1. 保留普通 Human / AI Message
    2. 保留完整 Tool Call → Tool Result 序列
    3. 删除未完成 Tool Call
    4. 删除孤立 ToolMessage

    注意：

    这里只清理“发送给 LLM 的上下文”。

    不修改 LangGraph State 本身，
    因此 Evidence Checker 仍然可以访问
    原始 Tool Results 和完整执行轨迹。
    """

    safe_messages = []

    index = 0

    while index < len(messages):

        message = messages[index]

        # ====================================================
        # AIMessage with tool_calls
        # ====================================================

        if (
            isinstance(
                message,
                AIMessage,
            )
            and getattr(
                message,
                "tool_calls",
                None,
            )
        ):

            tool_calls = (
                message.tool_calls
            )

            # 当前 AIMessage 期望收到的 Tool Call ID
            expected_ids = {
                call.get("id")
                for call in tool_calls
                if call.get("id")
            }

            tool_messages = []

            next_index = (
                index + 1
            )

            # ToolMessage 必须紧跟在
            # AIMessage(tool_calls) 后面
            while (
                next_index < len(messages)
                and isinstance(
                    messages[next_index],
                    ToolMessage,
                )
            ):

                tool_messages.append(
                    messages[next_index]
                )

                next_index += 1

            returned_ids = {
                getattr(
                    tool_message,
                    "tool_call_id",
                    None,
                )
                for tool_message
                in tool_messages
                if getattr(
                    tool_message,
                    "tool_call_id",
                    None,
                )
            }

            # =================================================
            # 完整 Tool Call
            # =================================================

            if (
                expected_ids
                and expected_ids.issubset(
                    returned_ids
                )
            ):

                safe_messages.append(
                    message
                )

                # 只保留真正属于当前
                # tool_calls 的 ToolMessage
                for tool_message in tool_messages:

                    tool_call_id = getattr(
                        tool_message,
                        "tool_call_id",
                        None,
                    )

                    if tool_call_id in expected_ids:

                        safe_messages.append(
                            tool_message
                        )

            # =================================================
            # 不完整 Tool Call
            # =================================================

            else:

                print(
                    "\n[Message Sanitizer]"
                )

                print(
                    "Removed incomplete "
                    "tool-call message"
                )

                print(
                    f"expected_ids="
                    f"{sorted(expected_ids)}"
                )

                print(
                    f"returned_ids="
                    f"{sorted(returned_ids)}"
                )

            # 跳过已经检查过的 ToolMessage
            index = next_index

            continue

        # ====================================================
        # Orphan ToolMessage
        # ====================================================

        if isinstance(
            message,
            ToolMessage,
        ):

            print(
                "\n[Message Sanitizer]"
            )

            print(
                "Removed orphan ToolMessage"
            )

            index += 1

            continue

        # ====================================================
        # Normal Message
        # ====================================================

        safe_messages.append(
            message
        )

        index += 1

    return safe_messages


# ============================================================
# Agent Executor Node
# ============================================================


def agent_executor_node(
    state: AgentState,
):
    """
    Agent 主执行节点。

    职责：

    1. 获取当前 MessagesState
    2. 清理不合法 Tool Call History
    3. 将 Tools bind 到 LLM
    4. 让模型决定：
       - 调用 Tool
       - 或直接 Final Answer
    5. 如果产生 Tool Call：
       tool_rounds += 1
    """

    # ========================================================
    # LLM
    # ========================================================

    llm = get_llm(
        temperature=0
    )

    llm_with_tools = (
        llm.bind_tools(
            tools
        )
    )

    # ========================================================
    # Raw Message History
    # ========================================================

    raw_messages = state.get(
        "messages",
        [],
    )

    # ========================================================
    # Sanitize Message History
    # ========================================================

    safe_history = (
        sanitize_messages_for_llm(
            raw_messages
        )
    )

    if (
        len(safe_history)
        != len(raw_messages)
    ):

        print(
            "\n[Agent]"
        )

        print(
            "Message history sanitized: "
            f"{len(raw_messages)} "
            f"→ {len(safe_history)}"
        )

    # ========================================================
    # System Message
    # ========================================================

    system_message = (
        SystemMessage(
            content=SYSTEM_PROMPT
        )
    )

    # ========================================================
    # LLM Messages
    # ========================================================

    messages = [
        system_message,
        *safe_history,
    ]

    # ========================================================
    # Invoke Agent
    # ========================================================

    response = (
        llm_with_tools.invoke(
            messages
        )
    )

    # ========================================================
    # Tool Calls
    # ========================================================

    tool_calls = getattr(
        response,
        "tool_calls",
        None,
    )

    # ========================================================
    # State Result
    # ========================================================

    result = {
        "messages": [
            response
        ]
    }

    # ========================================================
    # Has Tool Calls
    # ========================================================

    if tool_calls:

        current_rounds = state.get(
            "tool_rounds",
            0,
        )

        new_rounds = (
            current_rounds + 1
        )

        result[
            "tool_rounds"
        ] = new_rounds

        print(
            "\n[Agent] "
            f"Tool Round: "
            f"{current_rounds} "
            f"-> {new_rounds}"
        )

        print(
            "\n[Agent] "
            "Structured Tool Call:"
        )

        # ================================================
        # Tool Call Logging
        # ================================================

        for index, call in enumerate(
            tool_calls,
            start=1,
        ):

            tool_name = (
                call.get(
                    "name",
                    "unknown",
                )
            )

            args = (
                call.get(
                    "args",
                    {},
                )
            )

            try:

                args_text = (
                    json.dumps(
                        args,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

            except Exception:

                args_text = (
                    str(args)
                )

            # 防止 Evidence 太长把终端刷爆
            if (
                len(args_text)
                > 1200
            ):

                args_text = (
                    args_text[:1200]
                    +
                    "\n... [truncated]"
                )

            print(
                f"\n  Tool Call {index}"
            )

            print(
                f"  Tool: {tool_name}"
            )

            print(
                "  Args:"
            )

            print(
                args_text
            )

    # ========================================================
    # No Tool Calls
    # ========================================================

    else:

        print(
            "\n[Agent] "
            "No Tool Call "
            "→ Final Answer"
        )

    return result