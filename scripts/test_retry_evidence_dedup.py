from langchain_core.messages import (
    AIMessage,
)

from app.agent.nodes.tool_node import (
    tool_node,
)


QUERY = (
    "Agent tools guardrails "
    "permissions security"
)


def build_tool_call_message(
    call_id: str,
):
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name":
                    "company_search",

                "args": {
                    "company":
                        "OpenAI",

                    "query":
                        QUERY,

                    "k":
                        4,
                },

                "id":
                    call_id,

                "type":
                    "tool_call",
            }
        ],
    )


def main():

    print(
        "\n"
        "========================================"
    )

    print(
        "Retry Evidence Dedup Test"
    )

    print(
        "========================================"
    )

    # ========================================================
    # First Search
    # ========================================================

    print(
        "\n"
        "========== FIRST SEARCH =========="
    )

    first_ai_message = (
        build_tool_call_message(
            "test_call_1"
        )
    )

    state_1 = {
        "messages": [
            first_ai_message
        ],

        "evidence_ids": [],

        "new_evidence_count": 0,

        "duplicate_evidence_count": 0,
    }

    result_1 = tool_node(
        state_1
    )

    first_tool_messages = (
        result_1.get(
            "messages",
            [],
        )
    )

    print(
        "\nFirst Search:"
    )

    print(
        "Last New Evidence:",
        result_1.get(
            "last_new_evidence_count"
        ),
    )

    print(
        "Last Duplicate Evidence:",
        result_1.get(
            "last_duplicate_evidence_count"
        ),
    )

    print(
        "Total Unique Evidence:",
        len(
            result_1.get(
                "evidence_ids",
                [],
            )
        ),
    )

    # ========================================================
    # Second Search
    #
    # 完全相同 Query。
    # 应该被识别为重复 Evidence。
    # ========================================================

    print(
        "\n"
        "========== SECOND SEARCH =========="
    )

    second_ai_message = (
        build_tool_call_message(
            "test_call_2"
        )
    )

    state_2 = {
        "messages": [
            first_ai_message,
            *first_tool_messages,
            second_ai_message,
        ],

        "evidence_ids":
            result_1.get(
                "evidence_ids",
                [],
            ),

        "new_evidence_count":
            result_1.get(
                "new_evidence_count",
                0,
            ),

        "duplicate_evidence_count":
            result_1.get(
                "duplicate_evidence_count",
                0,
            ),
    }

    result_2 = tool_node(
        state_2
    )

    print(
        "\nSecond Search:"
    )

    print(
        "Last New Evidence:",
        result_2.get(
            "last_new_evidence_count"
        ),
    )

    print(
        "Last Duplicate Evidence:",
        result_2.get(
            "last_duplicate_evidence_count"
        ),
    )

    print(
        "Total Unique Evidence:",
        len(
            result_2.get(
                "evidence_ids",
                [],
            )
        ),
    )

    # ========================================================
    # Inspect Second Tool Result
    # ========================================================

    second_tool_messages = (
        result_2.get(
            "messages",
            [],
        )
    )

    print(
        "\nSecond Tool Result:\n"
    )

    for message in second_tool_messages:

        print(
            message.content
        )

    # ========================================================
    # Simple Assertions
    # ========================================================

    first_new = result_1.get(
        "last_new_evidence_count",
        0,
    )

    second_new = result_2.get(
        "last_new_evidence_count",
        0,
    )

    second_duplicates = (
        result_2.get(
            "last_duplicate_evidence_count",
            0,
        )
    )

    print(
        "\n"
        "========================================"
    )

    if (
        first_new > 0
        and second_new == 0
        and second_duplicates > 0
    ):

        print(
            "RESULT: PASS"
        )

    else:

        print(
            "RESULT: FAIL"
        )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()