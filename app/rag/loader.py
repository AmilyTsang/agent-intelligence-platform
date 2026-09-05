from pathlib import Path

import pymupdf
from langchain_core.documents import Document


def load_pdf(file_path: str | Path) -> list[Document]:
    """
    按页读取 PDF，并保留 source/page metadata。
    """

    file_path = Path(file_path)

    pdf = pymupdf.open(file_path)

    documents: list[Document] = []

    for page_index, page in enumerate(pdf):
        text = page.get_text("text").strip()

        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "page": page_index + 1,
                },
            )
        )

    pdf.close()

    return documents


def load_pdf_directory(
    directory: str | Path,
) -> list[Document]:
    """
    读取目录及子目录中的所有 PDF。
    """

    directory = Path(directory)

    all_documents: list[Document] = []

    for pdf_path in directory.rglob("*.pdf"):

        print(f"Loading: {pdf_path}")

        docs = load_pdf(pdf_path)

        # 使用 PDF 所在父目录作为 company metadata
        company = pdf_path.parent.name

        for doc in docs:
            doc.metadata["company"] = company

        all_documents.extend(docs)

    return all_documents