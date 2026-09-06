from app.agent.graph import research_graph


def main():

    print(
        "\nAgent Intelligence Platform\n"
    )

    while True:

        query = input(
            "User> "
        ).strip()

        if query.lower() in {
            "exit",
            "quit",
            "q",
        }:
            break

        if not query:
            continue

        try:

            result = research_graph.invoke(
                {
                    "query": query,
                }
            )

            print("\n========== RESULT ==========")

            print(
                f"Task Type: "
                f"{result.get('task_type')}"
            )

            print(
                f"Complexity: "
                f"{result.get('complexity')}"
            )

            if result.get("plan"):
                print("\nPlan:")

                for step in result["plan"]:
                    print(
                        f"{step['step_id']}. "
                        f"{step['description']}"
                    )

            print("\nAnswer:\n")

            print(
                result.get(
                    "answer",
                    "",
                )
            )

            print(
                "\n============================\n"
            )

        except Exception as exc:

            print(
                f"\nERROR: {exc}\n"
            )

            print(
                "\nEvidence Sufficient:",
                result.get(
                    "evidence_sufficient",
                ),
            )

            print(
                "Evidence Score:",
                result.get(
                    "evidence_score",
                ),
            )

            print(
                "Evidence Gaps:",
            )

            for index, gap in enumerate(
                result.get(
                    "evidence_gaps",
                    [],
                ),
                start=1,
            ):
                print(
                    f"{index}. {gap}"
                )


if __name__ == "__main__":
    main()