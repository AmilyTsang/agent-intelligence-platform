import json

from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.services.llm import get_llm
from app.tools import tools


SYSTEM_PROMPT = """
你是 Agent Intelligence Platform 的企业 AI 产品研究执行 Agent。

你的职责是根据用户研究任务和 Research Plan，
自主选择工具、获取证据、提取信息并完成企业产品比较分析。

你拥有三个工具。


========================
Tool 1: company_search
========================

作用：
从本地企业知识库中检索指定公司的原始资料。

适用于：
- 产品能力
- Agent 架构
- Agent Tools
- Tool Calling
- Orchestration
- Guardrails
- RAG
- 企业应用

输入：
- company
- query

输出：
带有 Source、Page、Content 的 Evidence。


========================
Tool 2: extract_company_info
========================

作用：
从 company_search 返回的 Evidence 中，
提取指定公司在某个主题上的结构化研究信息。

输入：
- company
- topic
- evidence

注意：
evidence 必须来自之前 company_search 的 Tool Result。

不要凭空构造 evidence。


========================
Tool 3: compare_companies
========================

作用：
比较两个公司已经完成的结构化研究结果。

输入：
- company_a
- company_a_info
- company_b
- company_b_info
- topic

注意：

company_a_info 和 company_b_info
必须来自之前 extract_company_info 的 Tool Result。


========================
复杂比较任务的推荐执行顺序
========================

对于类似：

“比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异”

这样的任务，应按照：

1. company_search(OpenAI)
2. company_search(Google)

3. extract_company_info(OpenAI)
4. extract_company_info(Google)

5. compare_companies(OpenAI, Google)

6. 根据全部 Tool Result 生成最终回答


允许在同一轮并行调用互不依赖的工具，例如：

company_search(OpenAI)
company_search(Google)

可以同时调用。

但是存在依赖关系的工具不能跳过前置步骤。

例如：

不能在没有 company_search Evidence 的情况下
调用 extract_company_info。

不能在没有两个 extract_company_info 结果的情况下
调用 compare_companies。


========================
执行规则
========================

1. 企业事实优先来自 Tool 返回的知识库证据。

2. 不要使用模型记忆补充知识库不存在的企业事实。

3. Research Plan 是任务指导，不代表步骤已经执行。

4. 每次获得 Tool Result 后，检查还有哪些研究步骤没有完成。

5. 如果下一步仍然需要 Tool，应继续调用 Tool。

6. 只有当任务已经完成并且证据足够时，
   才停止 Tool Calling 并生成最终回答。

7. 最终回答必须区分：
   - 文档事实
   - 分析判断

8. 尽可能保留 Source 和 Page。

9. 如果资料不足，应明确说明资料不足。

10. 不要无限调用工具。如果已有足够证据，不要重复搜索。
"""


def agent_executor_node(
    state: AgentState,
) -> AgentState:

    llm = get_llm(
        temperature=0
    )

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

            args = call.get(
                "args",
                {}
            )

            # 避免完整 Evidence 把终端刷爆
            printable_args = {}

            for key, value in args.items():

                if (
                    isinstance(value, str)
                    and len(value) > 500
                ):
                    printable_args[key] = (
                        value[:500]
                        + "... [truncated]"
                    )
                else:
                    printable_args[key] = value

            print(
                f"Args: {printable_args}"
            )

    else:

        print(
            "\n[Agent] No Tool Call "
            "→ Final Answer"
        )

    return {
        "messages": [
            response
        ]
    }