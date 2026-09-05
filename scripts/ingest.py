from pathlib import Path

from app.config import settings
from app.rag.loader import load_pdf_directory
from app.rag.splitter import split_documents
from app.rag.vector_store import build_vector_store


def main():
    companies_dir = settings.data_dir / "companies"

    if not companies_dir.exists():
        raise FileNotFoundError(
            f"数据目录不存在: {companies_dir}"
        )

    print("1. Loading documents...")

    documents = load_pdf_directory(
        companies_dir
    )

    print(
        f"Loaded {len(documents)} page documents."
    )

    print("2. Splitting documents...")

    chunks = split_documents(documents)

    print(
        f"Generated {len(chunks)} chunks."
    )

    print("3. Building vector store...")

    build_vector_store(chunks)

    print("Vector store created successfully.")


if __name__ == "__main__":
    main()