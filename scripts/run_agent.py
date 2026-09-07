import traceback

from app.agent.graph import (
    research_graph,
)


def print_result(
    result: dict,
):
    """
    打印 Research Agent 最终状态。
    """

    print(
        "\n"
        "============================"
    )

    print(
        "========== RESULT =========="
    )

    print(
        "============================"
    )

    # ========================================================
    # Router
    # ========================================================

    print(
        "\nTask Type:",
        result.get(
            "task_type"
        ),
    )

    print(
        "Complexity:",
        result.get(
            "complexity"
        ),
    )

    # ========================================================
    # Plan
    # ========================================================

    plan = result.get(
        "plan",
        [],
    )

    print(
        "\nPlan:"
    )

    if plan:

        for index, step in enumerate(
            plan,
            start=1,
        ):

            if isinstance(
                step,
                dict,
            ):

                description = (
                    step.get(
                        "description"
                    )
                    or step.get(
                        "action"
                    )
                    or str(step)
                )

            else:

                description = str(
                    step
                )

            print(
                f"{index}. "
                f"{description}"
            )

    else:

        print(
            "No research plan."
        )

    # ========================================================
    # Answer
    # ========================================================

    answer = result.get(
        "answer",
        "",
    )

    print(
        "\nAnswer:\n"
    )

    if answer:

        print(
            answer
        )

    else:

        print(
            "No final answer."
        )

    # ========================================================
    # Evidence Checker
    # ========================================================

    if (
        "evidence_sufficient"
        in result
    ):

        print(
            "\n"
            "----------------------------"
        )

        print(
            "Evidence Evaluation"
        )

        print(
            "----------------------------"
        )

        print(
            "\nEvidence Sufficient:",
            result.get(
                "evidence_sufficient"
            ),
        )

        print(
            "Evidence Score:",
            result.get(
                "evidence_score"
            ),
        )

        evidence_gaps = (
            result.get(
                "evidence_gaps",
                [],
            )
        )

        print(
            "\nEvidence Gaps:"
        )

        if evidence_gaps:

            for index, gap in enumerate(
                evidence_gaps,
                start=1,
            ):

                print(
                    f"{index}. {gap}"
                )

        else:

            print(
                "None"
            )

    # ========================================================
    # Retry
    # ========================================================

    print(
        "\n"
        "----------------------------"
    )

    print(
        "Retry Information"
    )

    print(
        "----------------------------"
    )

    print(
        "\nRetry Count:",
        result.get(
            "retry_count",
            0,
        ),
    )

    retry_queries = (
        result.get(
            "retry_queries",
            [],
        )
    )

    print(
        "\nLast Retry Queries:"
    )

    if retry_queries:

        for index, item in enumerate(
            retry_queries,
            start=1,
        ):

            if isinstance(
                item,
                dict,
            ):

                print(
                    f"\n{index}."
                )

                print(
                    "Company:",
                    item.get(
                        "company",
                        "",
                    ),
                )

                print(
                    "Query:",
                    item.get(
                        "query",
                        "",
                    ),
                )

                print(
                    "Gap:",
                    item.get(
                        "gap",
                        "",
                    ),
                )

            else:

                print(
                    f"{index}. {item}"
                )

    else:

        print(
            "None"
        )

    # ========================================================
    # Tool Rounds
    # ========================================================

    print(
        "\nTool Rounds "
        "(current attempt):",
        result.get(
            "tool_rounds",
            0,
        ),
    )

    print(
        "\n"
        "============================"
    )


def main():

    # ========================================================
    # Query
    # ========================================================

    print(
        "\n"
        "========================================"
    )

    print(
        "Agent Intelligence Platform"
    )

    print(
        "========================================"
    )

    query = input(
        "\n请输入研究问题："
    ).strip()

    if not query:

        print(
            "\nQuery cannot be empty."
        )

        return

    # ========================================================
    # Initial State
    # ========================================================

    initial_state = {
        "query": query,

        "messages": [],

        "tool_rounds": 0,

        "retry_count": 0,

        "retry_queries": [],
    }

    # ========================================================
    # Run Graph
    # ========================================================

    try:

        result = (
            research_graph.invoke(
                initial_state
            )
        )

    except Exception as exc:

        print(
            "\n"
            "============================"
        )

        print(
            "ERROR"
        )

        print(
            "============================"
        )

        print(
            f"\n{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            "\nTraceback:"
        )

        traceback.print_exc()

        # 非常重要：
        #
        # Graph 执行失败后 result
        # 没有成功创建。
        #
        # 因此这里必须 return，
        # 不能继续执行 result.get(...)
        return

    # ========================================================
    # Print Result
    # ========================================================

    print_result(
        result
    )


if __name__ == "__main__":
    main()