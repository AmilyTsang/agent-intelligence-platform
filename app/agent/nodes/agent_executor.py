import json

from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.services.llm import get_llm
from app.tools import tools


SYSTEM_PROMPT = """
你是 Agent Intelligence Platform 的企业 AI 产品研究执行 Agent。

你的职责是根据用户研究任务和 Research Plan，
自主选择工具、获取证据、提取信息、进行比较，
最终生成基于证据的企业 AI 产品研究结果。


========================
你拥有的工具
========================


Tool 1: company_search

作用：

从企业知识库中检索指定公司的原始资料。

适用于：

- Agent 产品能力
- Agent Tools
- Tool Calling
- Function Calling
- Orchestration
- RAG
- Guardrails
- 企业 AI 架构
- 产品技术能力

输入：

company
query

输出：

包含以下信息的 Evidence：

- Company
- Source
- Page
- Content


========================


Tool 2: extract_company_info

作用：

从 company_search 已经获取的 Evidence 中，
提取某家公司关于指定主题的结构化研究信息。

输入：

company
topic
evidence

其中：

evidence 必须来自之前实际执行完成的
company_search Tool Result。

禁止凭空构造 Evidence。


========================


Tool 3: compare_companies

作用：

比较两个公司已经完成的结构化研究结果。

输入：

company_a
company_a_info
company_b
company_b_info
topic

其中：

company_a_info 和 company_b_info

必须来自之前实际执行完成的：

extract_company_info Tool Result。


========================
复杂企业比较任务执行方式
========================

例如用户提出：

“比较 OpenAI 和 Google 在 Agent Tools 设计上的共同点和差异。”

通常应按照以下研究流程执行：

第一阶段：

company_search(OpenAI)

company_search(Google)


第二阶段：

extract_company_info(OpenAI)

extract_company_info(Google)


第三阶段：

compare_companies(
    OpenAI,
    Google
)


第四阶段：

根据全部 Tool Result
生成最终研究报告。


========================
并行调用规则
========================

不存在依赖关系的 Tool 可以在同一轮并行调用。

例如：

company_search(OpenAI)

company_search(Google)

可以在同一个 AIMessage 中同时调用。

同样：

extract_company_info(OpenAI)

extract_company_info(Google)

如果已经分别获得对应 Evidence，
也可以同时调用。


========================
依赖关系规则
========================

禁止跳过前置步骤。


错误示例：

没有执行 company_search，
直接调用 extract_company_info。


错误示例：

没有得到两个公司的结构化提取结果，
直接调用 compare_companies。


正确流程：

Search
→ Extract
→ Compare
→ Final


========================
Research Plan 使用规则
========================

Research Plan 只是任务执行指导。

Research Plan 中出现某一步，
不代表这一步已经真实执行。

例如 Plan 中写：

“提取 OpenAI Agent Tools 信息”

不意味着已经获得了提取结果。

只有对应 Tool Result
真正出现在 messages 中，
才代表该步骤已经完成。


========================
Evidence 规则
========================

1. 企业事实必须优先来自 Tool Result。

2. 不允许使用模型自身记忆补充
   企业知识库没有提供的事实。

3. 如果当前 Evidence 不足，
   必须明确说明资料不足。

4. “本次 Evidence 中没有发现”
   不等于
   “整份文档没有”。

5. 不要因为 Research Plan 中包含某个概念，
   就认为知识库一定存在该事实。


========================
停止规则
========================

每次 Tool 执行完成后：

检查当前任务是否还有必要继续调用 Tool。

如果仍然缺少完成研究任务所需的信息：

继续调用合适的 Tool。

如果已经完成：

停止 Tool Calling，
直接生成 Final Answer。

不要重复搜索已经获得充分证据的内容。

不要无限调用工具。


========================
最终回答要求
========================

最终回答：

1. 直接输出研究结论。

2. 不要输出：

   “我现在开始分析”
   “让我继续”
   “我已经完成研究步骤”

   等内部执行过程描述。

3. 明确区分：

   - 文档事实
   - 分析判断

4. 尽量保留：

   - Source
   - Page

5. 对 Evidence 不支持的结论明确说明：
   当前资料不足。
"""


def agent_executor_node(
    state: AgentState,
):
    """
    LangGraph 中的 Agent Executor。

    职责：

    1. 根据当前 Messages 和 Research Plan
       判断是否需要调用 Tool。

    2. 使用 bind_tools 生成 Structured Tool Calling。

    3. 如果产生 Tool Call：
       tool_rounds + 1。

    4. 如果没有 Tool Call：
       进入最终回答流程。
    """

    # ========================
    # LLM
    # ========================

    llm = get_llm(
        temperature=0
    )

    llm_with_tools = llm.bind_tools(
        tools
    )

    # ========================
    # Research Plan
    # ========================

    plan = state.get(
        "plan",
        [],
    )

    task_type = state.get(
        "task_type",
        "unknown",
    )

    complexity = state.get(
        "complexity",
        "unknown",
    )

    # ========================
    # System Message
    # ========================

    system_message = SystemMessage(
        content=(
            SYSTEM_PROMPT
            + "\n\n"
            + "========================\n"
            + "当前任务状态\n"
            + "========================\n"
            + f"Task Type: {task_type}\n"
            + f"Complexity: {complexity}\n"
            + "\nResearch Plan:\n"
            + json.dumps(
                plan,
                ensure_ascii=False,
                indent=2,
            )
        )
    )

    # ========================
    # Messages
    # ========================

    messages = [
        system_message,
        *state.get(
            "messages",
            [],
        ),
    ]

    # ========================
    # Agent Execution
    # ========================

    response = llm_with_tools.invoke(
        messages
    )

    # ========================
    # Structured Tool Calls
    # ========================

    tool_calls = getattr(
        response,
        "tool_calls",
        [],
    )

    # LangGraph 节点返回的是 partial state update
    result = {
        "messages": [
            response
        ],
    }

    # ========================
    # Tool Round Counter
    # ========================

    if tool_calls:

        current_rounds = state.get(
            "tool_rounds",
            0,
        )

        new_rounds = (
            current_rounds + 1
        )

        # 非常关键：
        # 必须把新值返回给 LangGraph，
        # 否则下一轮 state 中仍然是旧值。
        result["tool_rounds"] = (
            new_rounds
        )

        print(
            f"\n[Agent] Tool Round: "
            f"{current_rounds} -> {new_rounds}"
        )

        print(
            "[Agent] Structured Tool Call:"
        )

        for call in tool_calls:

            tool_name = call.get(
                "name",
                "unknown",
            )

            args = call.get(
                "args",
                {},
            )

            # Evidence / Extract Result 可能非常长，
            # 终端只打印前 500 字符。
            printable_args = {}

            for key, value in args.items():

                if (
                    isinstance(
                        value,
                        str,
                    )
                    and len(value) > 500
                ):
                    printable_args[key] = (
                        value[:500]
                        + "... [truncated]"
                    )

                else:

                    printable_args[key] = value

            print(
                f"Tool: {tool_name}"
            )

            print(
                f"Args: {printable_args}"
            )

    else:

        print(
            "\n[Agent] No Tool Call "
            "→ Final Answer"
        )

    return result