from app.agent.state import AgentState


def route_after_agent(
    state: AgentState,
) -> str:
    """
    判断 Agent 是否产生 Tool Call。
    """

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return "finalize"

    last_message = messages[-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        None,
    )

    if tool_calls:
        return "tools"

    return "finalize"