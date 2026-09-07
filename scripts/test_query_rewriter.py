from app.agent.nodes.query_rewriter import (
    query_rewriter_node,
)


def main():

    # ========================================================
    # Mock Agent State
    # ========================================================

    state = {
        "query": (
            "比较 OpenAI 和 Google "
            "在 Agent Tools 设计上的共同点和差异。"
        ),

        "plan": [
            {
                "step_id": 1,
                "action":
                    "retrieve_information",
                "description":
                    (
                        "检索 OpenAI 和 Google "
                        "Agent Tools 官方资料"
                    ),
            },
            {
                "step_id": 2,
                "action":
                    "extract_information",
                "description":
                    (
                        "提取工具定义、调用机制、"
                        "上下文管理、安全权限等维度"
                    ),
            },
            {
                "step_id": 3,
                "action":
                    "compare_information",
                "description":
                    (
                        "比较双方 Agent Tools "
                        "设计的共同点与差异"
                    ),
            },
        ],

        "evidence_sufficient":
            False,

        "evidence_score":
            0.62,

        "evidence_gaps": [
            (
                "当前已检索的 OpenAI Evidence "
                "未覆盖工具安全与权限控制相关内容。"
            ),
            (
                "当前已检索的 Google Evidence "
                "未覆盖工具错误处理与上下文管理机制。"
            ),
            (
                "当前双方 Evidence 均缺少 "
                "工具调用延迟、成功率和成本等"
                "量化指标。"
            ),
        ],

        "retry_count":
            0,
    }

    # ========================================================
    # Run Query Rewriter
    # ========================================================

    print(
        "\n========== "
        "QUERY REWRITER TEST "
        "==========\n"
    )

    result = query_rewriter_node(
        state
    )

    # ========================================================
    # Result
    # ========================================================

    print(
        "\n========== "
        "RESULT "
        "==========\n"
    )

    print(
        "Retry Queries:"
    )

    retry_queries = result.get(
        "retry_queries",
        [],
    )

    for index, item in enumerate(
        retry_queries,
        start=1,
    ):

        print(
            f"\n{index}."
        )

        print(
            "Company:",
            item.get("company"),
        )

        print(
            "Query:",
            item.get("query"),
        )

        print(
            "Gap:",
            item.get("gap"),
        )

    print(
        "\nRetry Reason:"
    )

    print(
        result.get(
            "retry_reason",
            "",
        )
    )


if __name__ == "__main__":
    main()