import json

from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.services.llm import get_llm
from app.tools import tools


SYSTEM_PROMPT = """
你是 Agent Intelligence Platform 的企业 AI 产品研究 Agent。

你的任务是根据用户问题和研究计划完成企业 AI 产品研究。

你可以调用 company_search 工具，从本地企业知识库中检索指定公司的公开资料。

执行原则：

1. 涉及企业产品、Agent 架构、Tools、Orchestration、
   Guardrails 等事实时，应优先调用 company_search 获取证据。

2. 不要凭模型已有知识直接编造企业事实。

3. company_search 的 company 参数应使用明确公司名称，
   例如 OpenAI 或 Google。

4. query 参数应描述真正需要检索的信息，
   不要只填写公司名称。

5. 如果研究多个公司，可以进行多次 Tool Calling。

6. 获得足够证据后，不再调用工具，直接生成答案。

7. 最终回答应尽可能保留 Source 和 Page。

8. 如果知识库证据不足，请明确说明资料不足。
"""


def agent_executor_node(
    state: AgentState,
) -> AgentState:

    llm = get_llm(
        temperature=0
    )

    # 关键：
    # 将 Tool Schema 绑定给 LLM
    llm_with_tools = llm.bind_tools(
        tools
    )

    plan = state.get(
        "plan",
        [],
    )

    system_message = SystemMessage(
        content=(
            SYSTEM_PROMPT
            + "\n\n当前任务类型：\n"
            + str(
                state.get(
                    "task_type",
                    "unknown",
                )
            )
            + "\n\nResearch Plan：\n"
            + json.dumps(
                plan,
                ensure_ascii=False,
                indent=2,
            )
        )
    )

    messages = [
        system_message,
        *state["messages"],
    ]

    response = llm_with_tools.invoke(
        messages
    )

    tool_calls = getattr(
        response,
        "tool_calls",
        [],
    )

    if tool_calls:

        print(
            "\n[Agent] Structured Tool Call:"
        )

        for call in tool_calls:

            print(
                f"Tool: {call.get('name')}"
            )

            print(
                f"Args: {call.get('args')}"
            )

    else:

        print(
            "\n[Agent] No Tool Call → Final Answer"
        )

    return {
        "messages": [
            response
        ]
    }