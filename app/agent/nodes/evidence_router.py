from app.agent.state import AgentState


MAX_RETRY = 2


def route_after_evidence_check(
    state: AgentState,
) -> str:
    """
    Evidence Checker 后的条件路由。

    返回：

        end:
            Evidence 已充分，
            没有可补充的 Evidence Gap，
            或已经达到 Retry 上限。

        retry:
            Evidence 不充分，
            且仍允许执行补充研究。
    """

    sufficient = state.get(
        "evidence_sufficient",
        False,
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    gaps = state.get(
        "evidence_gaps",
        [],
    )

    print(
        "\n[Evidence Router]"
    )

    print(
        f"sufficient={sufficient}, "
        f"retry_count={retry_count}, "
        f"MAX_RETRY={MAX_RETRY}"
    )

    # ======================================
    # Evidence 已充分
    # ======================================

    if sufficient:

        print(
            "[Evidence Router] "
            "Evidence sufficient → END"
        )

        return "end"

    # ======================================
    # 没有 Evidence Gap
    # ======================================

    if not gaps:

        print(
            "[Evidence Router] "
            "No Evidence Gaps → END"
        )

        return "end"

    # ======================================
    # Retry 上限
    # ======================================

    if retry_count >= MAX_RETRY:

        print(
            "[Evidence Router] "
            f"Retry limit reached "
            f"({retry_count}/{MAX_RETRY}) "
            "→ END"
        )

        return "end"

    # ======================================
    # Evidence 不足 → 补充研究
    # ======================================

    print(
        "[Evidence Router] "
        "Evidence insufficient "
        "→ Query Rewrite"
    )

    return "retry"