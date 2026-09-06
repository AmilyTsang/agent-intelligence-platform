from app.agent.state import AgentState


def finalize_node(
    state: AgentState,
) -> AgentState:
    """
    将 Agent 最后一条自然语言回答写入 answer。
    """

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return {
            "answer": ""
        }

    last_message = messages[-1]

    content = last_message.content

    if not isinstance(
        content,
        str,
    ):
        content = str(content)

    return {
        "answer": content
    }