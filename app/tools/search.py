import hashlib

from langchain_core.documents import Document

from app.rag.vector_store_cache import (
    get_vector_store,
)


# ============================================================
# Evidence ID
# ============================================================


def build_evidence_id(
    document: Document,
) -> str:
    """
    为 Document 生成稳定的 Evidence ID。

    优先使用：

        company
        source
        page
        chunk_id

    如果 chunk_id 不存在，
    再加入 content hash。

    这个 ID 后续还可以用于：
        Retry Evidence 去重
        Evaluation
        Source Tracking
        Frontend Evidence Trace
    """

    metadata = (
        document.metadata
        or {}
    )

    company = str(
        metadata.get(
            "company",
            "",
        )
    ).strip().lower()

    source = str(
        metadata.get(
            "source",
            "",
        )
    ).strip()

    page = str(
        metadata.get(
            "page",
            "",
        )
    ).strip()

    chunk_id = str(
        metadata.get(
            "chunk_id",
            "",
        )
    ).strip()

    content = (
        document.page_content
        or ""
    ).strip()

    # 如果已经有 chunk_id，
    # 直接使用 metadata 组合即可。
    if chunk_id:

        raw_key = (
            f"{company}|"
            f"{source}|"
            f"{page}|"
            f"{chunk_id}"
        )

    else:

        content_hash = (
            hashlib.sha1(
                content.encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
        )

        raw_key = (
            f"{company}|"
            f"{source}|"
            f"{page}|"
            f"{content_hash}"
        )

    return raw_key


# ============================================================
# Document Deduplication
# ============================================================


def deduplicate_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Document 级去重。

    如果多个 Retrieval Result
    指向同一个：

        company
        source
        page
        chunk_id

    只保留第一次出现的结果。

    FAISS similarity_search 返回结果本身是按相关性排序，
    所以第一次出现通常就是优先级最高的版本。
    """

    seen = set()

    unique_documents = []

    for document in documents:

        evidence_id = (
            build_evidence_id(
                document
            )
        )

        if evidence_id in seen:
            continue

        seen.add(
            evidence_id
        )

        unique_documents.append(
            document
        )

    return unique_documents


# ============================================================
# Page Diversity
# ============================================================


def select_diverse_documents(
    documents: list[Document],
    k: int,
) -> list[Document]:
    """
    基础 Page Diversity。

    第一轮：
        尽量优先选择不同 source/page。

    第二轮：
        如果不同页面数量不足 k，
        再按照原始相关性顺序补齐。

    示例：

    原始结果：

        p25 chunk 1
        p25 chunk 2
        p25 chunk 3
        p26 chunk 1
        p31 chunk 1

    k=4

    Diversity 后优先：

        p25 chunk 1
        p26 chunk 1
        p31 chunk 1

    然后补：

        p25 chunk 2

    这样可以降低同一页高度相似 Evidence
    占满 Retrieval Context 的概率。
    """

    if k <= 0:
        return []

    selected = []

    selected_ids = set()

    seen_pages = set()

    # ========================================================
    # Pass 1
    # 优先不同 source/page
    # ========================================================

    for document in documents:

        metadata = (
            document.metadata
            or {}
        )

        source = str(
            metadata.get(
                "source",
                "",
            )
        ).strip()

        page = str(
            metadata.get(
                "page",
                "",
            )
        ).strip()

        page_key = (
            source,
            page,
        )

        if page_key in seen_pages:
            continue

        evidence_id = (
            build_evidence_id(
                document
            )
        )

        selected.append(
            document
        )

        selected_ids.add(
            evidence_id
        )

        seen_pages.add(
            page_key
        )

        if len(selected) >= k:
            return selected

    # ========================================================
    # Pass 2
    # 不同页面不够时补齐
    # ========================================================

    for document in documents:

        evidence_id = (
            build_evidence_id(
                document
            )
        )

        if evidence_id in selected_ids:
            continue

        selected.append(
            document
        )

        selected_ids.add(
            evidence_id
        )

        if len(selected) >= k:
            break

    return selected


# ============================================================
# Company Search
# ============================================================


def search_company_documents(
    company: str,
    query: str,
    k: int = 4,
) -> list[Document]:
    """
    从指定公司的本地知识库中进行向量检索。

    当前流程：

        Query
        ↓
        FAISS Candidate Retrieval
        ↓
        Metadata Filter
        ↓
        Chunk Deduplication
        ↓
        Page Diversity
        ↓
        Top-k Evidence

    注意：

    当前使用的是 LangChain FAISS。

    metadata filter 并不等同于
    数据库级真正 pre-filter。

    因此这里扩大 candidate 数量，
    再执行本地去重和 diversity。
    """

    # ========================================================
    # Normalize Input
    # ========================================================

    company_key = (
        company
        .strip()
        .lower()
    )

    query = (
        query
        .strip()
    )

    if not company_key:

        print(
            "\n[Search] "
            "Empty company."
        )

        return []

    if not query:

        print(
            "\n[Search] "
            "Empty query."
        )

        return []

    if k <= 0:

        print(
            "\n[Search] "
            "k <= 0."
        )

        return []

    # ========================================================
    # Cached Vector Store
    # ========================================================

    vector_store = (
        get_vector_store()
    )

    # ========================================================
    # Candidate Size
    # ========================================================

    # 最终要 4 条 Evidence 时，
    # 先尝试获得更多候选。
    #
    # 注意：
    # FAISS metadata filter 的具体实现
    # 可能导致实际返回数量小于 candidate_k。
    candidate_k = max(
        12,
        k * 4,
    )

    fetch_k = max(
        40,
        candidate_k * 4,
    )

    print(
        "\n[Search]"
    )

    print(
        f"company={company_key}"
    )

    print(
        f"query={query}"
    )

    print(
        f"target_k={k}, "
        f"candidate_k={candidate_k}, "
        f"fetch_k={fetch_k}"
    )

    # ========================================================
    # FAISS Retrieval
    # ========================================================

    candidates = (
        vector_store.similarity_search(
            query=query,
            k=candidate_k,
            filter={
                "company":
                    company_key
            },
            fetch_k=fetch_k,
        )
    )

    print(
        "[Search] "
        f"raw_candidates="
        f"{len(candidates)}"
    )

    # ========================================================
    # Deduplication
    # ========================================================

    unique_candidates = (
        deduplicate_documents(
            candidates
        )
    )

    duplicate_count = (
        len(candidates)
        -
        len(unique_candidates)
    )

    print(
        "[Search] "
        f"unique_candidates="
        f"{len(unique_candidates)}"
    )

    print(
        "[Search] "
        f"duplicates_removed="
        f"{duplicate_count}"
    )

    # ========================================================
    # Diversity Selection
    # ========================================================

    selected_documents = (
        select_diverse_documents(
            unique_candidates,
            k=k,
        )
    )

    print(
        "[Search] "
        f"selected="
        f"{len(selected_documents)}"
    )

    # ========================================================
    # Logging Selected Evidence
    # ========================================================

    for index, document in enumerate(
        selected_documents,
        start=1,
    ):

        metadata = (
            document.metadata
            or {}
        )

        source = metadata.get(
            "source",
            "unknown",
        )

        page = metadata.get(
            "page",
            "unknown",
        )

        chunk_id = metadata.get(
            "chunk_id",
            "unknown",
        )

        print(
            f"[Search] "
            f"Evidence {index}: "
            f"source={source}, "
            f"page={page}, "
            f"chunk_id={chunk_id}"
        )

    return selected_documents