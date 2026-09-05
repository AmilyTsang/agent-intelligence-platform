from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.rag.embeddings import get_embeddings


_vector_store = None


def build_vector_store(
    documents: list[Document],
) -> FAISS:
    """
    根据文档创建 FAISS 向量库，并保存到本地。

    Args:
        documents:
            已经切分完成的 Document 列表

    Returns:
        FAISS vector store
    """

    if not documents:
        raise ValueError(
            "documents 不能为空，无法创建向量库"
        )

    print(
        f"Creating vector store from {len(documents)} documents..."
    )

    # 获取 embedding 模型
    embeddings = get_embeddings()

    # 创建 FAISS
    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )

    # ==============================
    # 创建保存目录
    # ==============================

    vector_store_path = Path(
        settings.vector_store_dir
    )

    vector_store_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Saving vector store to: {vector_store_path}"
    )

    # 保存 FAISS 文件
    vector_store.save_local(
        folder_path=str(vector_store_path),
        index_name="index",
    )

    print(
        "Vector store saved successfully."
    )

    return vector_store



def load_vector_store() -> FAISS:
    """
    从本地加载 FAISS 向量库。
    """

    global _vector_store


    if _vector_store is not None:
        return _vector_store


    vector_store_path = Path(
        settings.vector_store_dir
    )


    if not vector_store_path.exists():

        raise FileNotFoundError(
            f"Vector store not found: {vector_store_path}\n"
            "Please run scripts.ingest first."
        )


    print(
        f"Loading vector store from: {vector_store_path}"
    )


    embeddings = get_embeddings()


    _vector_store = FAISS.load_local(
        folder_path=str(vector_store_path),
        embeddings=embeddings,
        index_name="index",
        allow_dangerous_deserialization=True,
    )


    print(
        "Vector store loaded successfully."
    )


    return _vector_store