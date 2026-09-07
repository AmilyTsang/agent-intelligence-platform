import re


EVIDENCE_BLOCK_PATTERN = re.compile(
    r"<<EVIDENCE_START>>\s*"
    r"(.*?)"
    r"\s*<<EVIDENCE_END>>",
    re.DOTALL,
)

EVIDENCE_ID_PATTERN = re.compile(
    r"^evidence_id:\s*(.+?)\s*$",
    re.MULTILINE,
)


def extract_evidence_blocks(
    content: str,
) -> list[dict]:
    """
    从 company_search Tool Result 中
    提取结构化 Evidence Block。

    返回：

    [
        {
            "evidence_id": "...",
            "content": "..."
        }
    ]
    """

    if not content:
        return []

    matches = (
        EVIDENCE_BLOCK_PATTERN
        .findall(content)
    )

    results = []

    for block in matches:

        id_match = (
            EVIDENCE_ID_PATTERN
            .search(block)
        )

        if not id_match:
            continue

        evidence_id = (
            id_match
            .group(1)
            .strip()
        )

        normalized_block = (
            "<<EVIDENCE_START>>\n"
            + block.strip()
            + "\n<<EVIDENCE_END>>"
        )

        results.append(
            {
                "evidence_id":
                    evidence_id,

                "content":
                    normalized_block,
            }
        )

    return results


def filter_new_evidence(
    content: str,
    seen_evidence_ids: set[str],
):
    """
    根据已经出现过的 Evidence IDs，
    过滤 company_search 的 Tool Result。

    Returns:

        filtered_content
        new_ids
        duplicate_ids
    """

    evidence_blocks = (
        extract_evidence_blocks(
            content
        )
    )

    # 不是 company_search 的 Evidence 格式
    if not evidence_blocks:
        return (
            content,
            [],
            [],
        )

    new_blocks = []
    new_ids = []
    duplicate_ids = []

    for item in evidence_blocks:

        evidence_id = item[
            "evidence_id"
        ]

        if (
            evidence_id
            in seen_evidence_ids
        ):
            duplicate_ids.append(
                evidence_id
            )

            continue

        # 同一个 Tool Result 内也立即加入，
        # 防止同批次重复。
        seen_evidence_ids.add(
            evidence_id
        )

        new_ids.append(
            evidence_id
        )

        new_blocks.append(
            item["content"]
        )

    # ========================================================
    # 全部是重复 Evidence
    # ========================================================

    if not new_blocks:

        filtered_content = """
No new evidence found.

All retrieved evidence chunks were already present
in the current research context.

Do not interpret this as evidence that the company
does not support the requested capability.

Consider:
- using a different retrieval query
- researching another missing dimension
- or finalizing if the current knowledge base
  cannot provide additional evidence
""".strip()

        return (
            filtered_content,
            new_ids,
            duplicate_ids,
        )

    # ========================================================
    # 返回真正新增的 Evidence
    # ========================================================

    filtered_content = (
        "\n\n".join(
            new_blocks
        )
    )

    return (
        filtered_content,
        new_ids,
        duplicate_ids,
    )