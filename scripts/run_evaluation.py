import json
import time
import traceback
from pathlib import Path
from datetime import datetime

from langchain_core.messages import AIMessage

from app.agent.graph import research_graph


# ============================================================
# Paths
# ============================================================


ROOT_DIR = Path(__file__).resolve().parent.parent

TEST_CASE_PATH = (
    ROOT_DIR
    / "evals"
    / "test_cases.json"
)

RESULT_DIR = (
    ROOT_DIR
    / "evals"
    / "results"
)

MAX_RETRY = 2


# ============================================================
# Load Test Cases
# ============================================================


def load_test_cases():

    with open(
        TEST_CASE_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# ============================================================
# Tool Trace
# ============================================================


def extract_tool_names(
    messages,
):
    """
    从 MessagesState 中提取 Agent
    实际提出过的 Structured Tool Calls。
    """

    tool_names = []

    for message in messages:

        if not isinstance(
            message,
            AIMessage,
        ):
            continue

        tool_calls = getattr(
            message,
            "tool_calls",
            None,
        )

        if not tool_calls:
            continue

        for call in tool_calls:

            name = call.get(
                "name"
            )

            if name:
                tool_names.append(
                    name
                )

    return tool_names


# ============================================================
# Check Expected Tools
# ============================================================


def evaluate_tools(
    actual_tools,
    expected_tools,
):
    """
    只要求 expected_tools
    至少出现一次。

    不要求 Tool Call 顺序完全固定，
    避免 Evaluation 过度脆弱。
    """

    missing = []

    actual_set = set(
        actual_tools
    )

    for tool_name in expected_tools:

        if tool_name not in actual_set:

            missing.append(
                tool_name
            )

    return (
        len(missing) == 0,
        missing,
    )


# ============================================================
# Single Case
# ============================================================


def run_case(
    case,
):
    """
    执行单条 Evaluation Case。
    """

    case_id = case[
        "id"
    ]

    query = case[
        "query"
    ]

    print(
        "\n"
        "========================================"
    )

    print(
        f"CASE: {case_id}"
    )

    print(
        "========================================"
    )

    print(
        f"\nQuery: {query}"
    )

    start = time.perf_counter()

    # ========================================================
    # Graph Execution
    # ========================================================

    try:

        result = research_graph.invoke(
            {
                "query": query,

                "messages": [],

                "tool_rounds": 0,

                "retry_count": 0,

                "retry_queries": [],

                "evidence_ids": [],

                "new_evidence_count": 0,

                "duplicate_evidence_count": 0,

                "last_new_evidence_count": 0,

                "last_duplicate_evidence_count": 0,
            }
        )

        execution_success = True

        error = None

    except Exception as exc:

        execution_success = False

        result = {}

        error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        print(
            f"\nERROR: {error}"
        )

        traceback.print_exc()

    elapsed = (
        time.perf_counter()
        -
        start
    )

    # ========================================================
    # Actual State
    # ========================================================

    actual_task_type = result.get(
        "task_type"
    )

    actual_complexity = result.get(
        "complexity"
    )

    retry_count = result.get(
        "retry_count",
        0,
    )

    evidence_sufficient = result.get(
        "evidence_sufficient"
    )

    evidence_score = result.get(
        "evidence_score"
    )

    messages = result.get(
        "messages",
        [],
    )

    actual_tools = (
        extract_tool_names(
            messages
        )
    )

    # ========================================================
    # Evaluation
    # ========================================================

    checks = {}

    # Graph
    checks[
        "execution_success"
    ] = execution_success

    # Router task type
    checks[
        "task_type"
    ] = (
        actual_task_type
        ==
        case.get(
            "expected_task_type"
        )
    )

    # Complexity
    checks[
        "complexity"
    ] = (
        actual_complexity
        ==
        case.get(
            "expected_complexity"
        )
    )

    # Tools
    (
        tool_check,
        missing_tools,
    ) = evaluate_tools(
        actual_tools=actual_tools,
        expected_tools=case.get(
            "expected_tools",
            [],
        ),
    )

    checks[
        "tools"
    ] = tool_check

    # Evidence Checker
    expect_evidence_checker = (
        case.get(
            "expect_evidence_checker",
            False,
        )
    )

    actual_evidence_checker = (
        "evidence_sufficient"
        in result
    )

    checks[
        "evidence_checker"
    ] = (
        actual_evidence_checker
        ==
        expect_evidence_checker
    )

    # Retry
    expect_retry = case.get(
        "expect_retry",
        False,
    )

    actual_retry = (
        retry_count > 0
    )

    checks[
        "retry_trigger"
    ] = (
        actual_retry
        ==
        expect_retry
    )

    # Retry Bound
    checks[
        "retry_limit"
    ] = (
        retry_count
        <= MAX_RETRY
    )

    # Optional final evidence expectation
    expected_evidence = (
        case.get(
            "expected_final_evidence_sufficient"
        )
    )

    if (
        expected_evidence
        is not None
    ):

        checks[
            "final_evidence"
        ] = (
            evidence_sufficient
            ==
            expected_evidence
        )

    # ========================================================
    # Overall Result
    # ========================================================

    passed = all(
        checks.values()
    )

    # ========================================================
    # Print
    # ========================================================

    print(
        "\n--- Evaluation ---"
    )

    print(
        "Execution:",
        execution_success,
    )

    print(
        "Task Type:",
        actual_task_type,
    )

    print(
        "Complexity:",
        actual_complexity,
    )

    print(
        "Tools:",
        actual_tools,
    )

    print(
        "Retry Count:",
        retry_count,
    )

    print(
        "Evidence Sufficient:",
        evidence_sufficient,
    )

    print(
        "Evidence Score:",
        evidence_score,
    )

    print(
        f"Elapsed: "
        f"{elapsed:.2f}s"
    )

    print(
        "\nChecks:"
    )

    for name, value in checks.items():

        print(
            f"  {name}: "
            f"{'PASS' if value else 'FAIL'}"
        )

    if missing_tools:

        print(
            "Missing Tools:",
            missing_tools,
        )

    print(
        "\nRESULT:",
        "PASS"
        if passed
        else "FAIL",
    )

    # ========================================================
    # Result Record
    # ========================================================

    return {
        "id":
            case_id,

        "query":
            query,

        "passed":
            passed,

        "execution_success":
            execution_success,

        "error":
            error,

        "elapsed_seconds":
            round(
                elapsed,
                2,
            ),

        "expected": {
            "task_type":
                case.get(
                    "expected_task_type"
                ),

            "complexity":
                case.get(
                    "expected_complexity"
                ),

            "tools":
                case.get(
                    "expected_tools",
                    [],
                ),

            "expect_evidence_checker":
                expect_evidence_checker,

            "expect_retry":
                expect_retry,

            "expected_final_evidence_sufficient":
                expected_evidence,
        },

        "actual": {
            "task_type":
                actual_task_type,

            "complexity":
                actual_complexity,

            "tools":
                actual_tools,

            "retry_count":
                retry_count,

            "evidence_sufficient":
                evidence_sufficient,

            "evidence_score":
                evidence_score,

            "unique_evidence":
                len(
                    result.get(
                        "evidence_ids",
                        [],
                    )
                ),

            "new_evidence_count":
                result.get(
                    "new_evidence_count",
                    0,
                ),

            "duplicate_evidence_count":
                result.get(
                    "duplicate_evidence_count",
                    0,
                ),
        },

        "checks":
            checks,

        "missing_tools":
            missing_tools,
    }


# ============================================================
# Summary
# ============================================================


def build_summary(
    results,
):
    total = len(
        results
    )

    passed = sum(
        1
        for item in results
        if item["passed"]
    )

    failed = (
        total - passed
    )

    execution_success = sum(
        1
        for item in results
        if item[
            "execution_success"
        ]
    )

    router_task_pass = sum(
        1
        for item in results
        if item[
            "checks"
        ].get(
            "task_type",
            False,
        )
    )

    complexity_pass = sum(
        1
        for item in results
        if item[
            "checks"
        ].get(
            "complexity",
            False,
        )
    )

    tool_pass = sum(
        1
        for item in results
        if item[
            "checks"
        ].get(
            "tools",
            False,
        )
    )

    retry_limit_pass = sum(
        1
        for item in results
        if item[
            "checks"
        ].get(
            "retry_limit",
            False,
        )
    )

    return {
        "total_cases":
            total,

        "passed_cases":
            passed,

        "failed_cases":
            failed,

        "pass_rate":
            round(
                passed / total,
                4,
            )
            if total
            else 0,

        "graph_execution_success_rate":
            round(
                execution_success / total,
                4,
            )
            if total
            else 0,

        "task_type_accuracy":
            round(
                router_task_pass / total,
                4,
            )
            if total
            else 0,

        "complexity_accuracy":
            round(
                complexity_pass / total,
                4,
            )
            if total
            else 0,

        "tool_expectation_pass_rate":
            round(
                tool_pass / total,
                4,
            )
            if total
            else 0,

        "retry_limit_pass_rate":
            round(
                retry_limit_pass / total,
                4,
            )
            if total
            else 0,
    }


# ============================================================
# Main
# ============================================================


def main():

    test_cases = (
        load_test_cases()
    )

    print(
        "\n"
        "========================================"
    )

    print(
        "Agent Intelligence Platform Evaluation"
    )

    print(
        "========================================"
    )

    print(
        f"\nTest Cases: "
        f"{len(test_cases)}"
    )

    results = []

    for case in test_cases:

        result = run_case(
            case
        )

        results.append(
            result
        )

    summary = build_summary(
        results
    )

    # ========================================================
    # Save
    # ========================================================

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    output_path = (
        RESULT_DIR
        /
        f"evaluation_{timestamp}.json"
    )

    output = {
        "generated_at":
            datetime.now()
            .isoformat(),

        "summary":
            summary,

        "results":
            results,
    }

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # ========================================================
    # Summary
    # ========================================================

    print(
        "\n"
        "========================================"
    )

    print(
        "EVALUATION SUMMARY"
    )

    print(
        "========================================"
    )

    for key, value in summary.items():

        print(
            f"{key}: {value}"
        )

    print(
        "\nSaved:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()