import time

from app.rag.vector_store_cache import (
    clear_vector_store_cache,
)

from app.tools.search import (
    search_company_documents,
)


def run_search(
    company: str,
    query: str,
):
    """
    执行一次 Search，
    并记录耗时。
    """

    start = time.perf_counter()

    documents = (
        search_company_documents(
            company=company,
            query=query,
            k=4,
        )
    )

    elapsed = (
        time.perf_counter()
        -
        start
    )

    print(
        "\n"
        "----------------------------"
    )

    print(
        f"Company: {company}"
    )

    print(
        f"Query: {query}"
    )

    print(
        f"Documents: "
        f"{len(documents)}"
    )

    print(
        f"Elapsed: "
        f"{elapsed:.2f}s"
    )

    print(
        "----------------------------"
    )

    return documents


def main():

    print(
        "\n"
        "========================================"
    )

    print(
        "Vector Store Cache "
        "+ Retrieval Diversity Test"
    )

    print(
        "========================================"
    )

    # ========================================================
    # 清空缓存
    # ========================================================

    clear_vector_store_cache()

    # ========================================================
    # Search 1
    #
    # 应该触发 Vector Store 初始化
    # ========================================================

    print(
        "\n"
        "========== SEARCH 1 =========="
    )

    run_search(
        company="OpenAI",
        query=(
            "Agent tools guardrails "
            "permissions security"
        ),
    )

    # ========================================================
    # Search 2
    #
    # 不应该重新初始化 Vector Store
    # ========================================================

    print(
        "\n"
        "========== SEARCH 2 =========="
    )

    run_search(
        company="Google",
        query=(
            "ADK tools error handling "
            "context management"
        ),
    )

    # ========================================================
    # Search 3
    #
    # Retry 风格 Query
    # ========================================================

    print(
        "\n"
        "========== SEARCH 3 =========="
    )

    run_search(
        company="OpenAI",
        query=(
            "API latency throughput "
            "rate limits performance"
        ),
    )

    print(
        "\n"
        "========================================"
    )

    print(
        "TEST COMPLETE"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()