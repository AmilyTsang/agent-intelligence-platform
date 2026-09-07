from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            "。",
            ". ",
            " ",
            "",
        ],
    )


def parse_pdf(
    *,
    file_path: Path,
    document_id: str,
    filename: str,
) -> tuple[list[Document], int]:
    """
    Parse PDF -> pages -> chunks.

    Returns:
        chunks,
        page_count
    """

    loader = PyPDFLoader(
        str(file_path)
    )

    pages = loader.load()

    page_count = len(
        pages
    )

    if page_count == 0:
        raise ValueError(
            "PDF 中没有可读取的页面。"
        )


    # ========================================================
    # Normalize Page Metadata
    # ========================================================

    normalized_pages: list[Document] = []


    for index, page in enumerate(
        pages
    ):
        content = (
            page.page_content
            or ""
        ).strip()


        if not content:
            continue


        raw_page_number = (
            page.metadata.get(
                "page"
            )
        )


        if isinstance(
            raw_page_number,
            int,
        ):
            page_number = (
                raw_page_number
                + 1
            )

        else:
            page_number = (
                index
                + 1
            )


        normalized_pages.append(
            Document(
                page_content=content,

                metadata={
                    "document_id":
                        document_id,

                    "filename":
                        filename,

                    "page":
                        page_number,

                    "source":
                        filename,
                },
            )
        )


    if not normalized_pages:
        raise ValueError(
            "PDF 中没有提取到可用于检索的文本。"
        )


    # ========================================================
    # Chunk
    # ========================================================

    splitter = (
        get_text_splitter()
    )


    chunks = (
        splitter.split_documents(
            normalized_pages
        )
    )


    if not chunks:
        raise ValueError(
            "PDF 文本切分后没有生成有效 Chunk。"
        )


    # ========================================================
    # Chunk ID
    # ========================================================

    page_chunk_counters = defaultdict(
        int
    )


    normalized_chunks: list[
        Document
    ] = []


    for chunk in chunks:
        page_number = int(
            chunk.metadata.get(
                "page",
                0,
            )
            or 0
        )


        page_chunk_counters[
            page_number
        ] += 1


        page_chunk_index = (
            page_chunk_counters[
                page_number
            ]
        )


        chunk_id = (
            f"{document_id}"
            f"_p{page_number}"
            f"_c{page_chunk_index}"
        )


        normalized_chunks.append(
            Document(
                page_content=(
                    chunk.page_content
                ),

                metadata={
                    **chunk.metadata,

                    "document_id":
                        document_id,

                    "filename":
                        filename,

                    "page":
                        page_number,

                    "chunk_id":
                        chunk_id,

                    "source":
                        filename,
                },
            )
        )


    return (
        normalized_chunks,
        page_count,
    )