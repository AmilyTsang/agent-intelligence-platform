from app.agent.graph import research_graph
from app.agent.nodes.evidence_checker import (
    evidence_checker_node,
)


def main():
    query = (
        "比较 OpenAI 和 Google "
        "在 Agent Tools 设计上的共同点和差异。"
    )

    print("\n========== RUN RESEARCH AGENT ==========\n")

    state = research_graph.invoke(
        {
            "query": query,
            "messages": [],
            "tool_rounds": 0,
        }
    )

    print("\n========== AGENT FINISHED ==========\n")

    print(
        "Task Type:",
        state.get("task_type"),
    )

    print(
        "Complexity:",
        state.get("complexity"),
    )

    print(
        "\nCandidate Answer:\n"
    )

    print(
        state.get(
            "answer",
            "No answer",
        )
    )

    # ======================================
    # Evidence Checker
    # ======================================

    print(
        "\n========== EVIDENCE CHECK ==========\n"
    )

    check_result = evidence_checker_node(
        state
    )

    print(
        "\n========== CHECK RESULT ==========\n"
    )

    print(
        "Evidence Sufficient:",
        check_result.get(
            "evidence_sufficient"
        ),
    )

    print(
        "Evidence Score:",
        check_result.get(
            "evidence_score"
        ),
    )

    print(
        "Evidence Gaps:"
    )

    gaps = check_result.get(
        "evidence_gaps",
        [],
    )

    if gaps:

        for index, gap in enumerate(
            gaps,
            start=1,
        ):
            print(
                f"{index}. {gap}"
            )

    else:

        print(
            "None"
        )


if __name__ == "__main__":
    main()