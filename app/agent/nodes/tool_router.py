MAX_TOOL_ROUNDS = 6


def route_after_agent(state):

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

    if not tool_calls:
        return "finalize"

    tool_rounds = state.get(
        "tool_rounds",
        0,
    )

    print(
        f"[Tool Router] "
        f"tool_rounds={tool_rounds}, "
        f"MAX_TOOL_ROUNDS={MAX_TOOL_ROUNDS}"
    )

    if tool_rounds > MAX_TOOL_ROUNDS:

        print(
            f"[Agent] Tool round limit reached: "
            f"{tool_rounds - 1}/"
            f"{MAX_TOOL_ROUNDS}"
        )

        return "force_finalize"

    return "tools"